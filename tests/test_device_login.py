import contextlib
import importlib.util
import io
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "charts/hermes-agent/files/device_login.py"


def load_script():
    spec = importlib.util.spec_from_file_location("device_login_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeAuthError(Exception):
    def __init__(self, code, *, relogin_required):
        super().__init__(code)
        self.code = code
        self.relogin_required = relogin_required


class OpenAICodexFlowTests(unittest.TestCase):
    def test_success_uses_native_store_without_logging_secrets(self):
        module = load_script()
        module.NOTIFY = "logs"
        save_tokens = mock.Mock()
        resolve = mock.Mock(
            side_effect=FakeAuthError("codex_auth_missing", relogin_required=True)
        )
        module._codex_native = mock.Mock(
            return_value=("client-id", "https://issuer.example/oauth/token", save_tokens, resolve)
        )
        module._post_json_status = mock.Mock(
            side_effect=[
                (
                    200,
                    {
                        "user_code": "ABCD-EFGH",
                        "device_auth_id": "secret-device-id",
                        "interval": 3,
                    },
                    {},
                ),
                (
                    200,
                    {
                        "authorization_code": "secret-authorization-code",
                        "code_verifier": "secret-code-verifier",
                    },
                    {},
                ),
            ]
        )
        module._post_form_status = mock.Mock(
            return_value=(
                200,
                {
                    "access_token": "secret-access-token",
                    "refresh_token": "secret-refresh-token",
                },
                {},
            )
        )
        module.notify_post = mock.Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            module.HERMES_HOME = Path(tmpdir)
            with mock.patch.object(module.time, "sleep"), contextlib.redirect_stdout(
                io.StringIO()
            ) as captured:
                result = module.run_openai_codex_flow()

        self.assertEqual(result, 0)
        save_tokens.assert_called_once()
        saved = save_tokens.call_args.args[0]
        self.assertEqual(saved["access_token"], "secret-access-token")
        self.assertEqual(saved["refresh_token"], "secret-refresh-token")
        output = captured.getvalue()
        self.assertIn("ABCD-EFGH", output)
        for secret in (
            "secret-device-id",
            "secret-authorization-code",
            "secret-code-verifier",
            "secret-access-token",
            "secret-refresh-token",
        ):
            self.assertNotIn(secret, output)

    def test_prompt_names_the_release_so_parallel_logins_are_distinguishable(self):
        module = load_script()
        module.NOTIFY = "logs"
        module.LOGIN_LABEL = "may"
        module._codex_native = mock.Mock(
            return_value=(
                "client-id",
                "https://issuer.example/oauth/token",
                mock.Mock(),
                mock.Mock(side_effect=FakeAuthError("codex_auth_missing", relogin_required=True)),
            )
        )
        module._post_json_status = mock.Mock(
            side_effect=[
                (200, {"user_code": "ABCD-EFGH", "device_auth_id": "id", "interval": 3}, {}),
                (200, {"authorization_code": "code", "code_verifier": "verifier"}, {}),
            ]
        )
        module._post_form_status = mock.Mock(
            return_value=(200, {"access_token": "a", "refresh_token": "r"}, {})
        )
        module.notify_post = mock.Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            module.HERMES_HOME = Path(tmpdir)
            with mock.patch.object(module.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                module.run_openai_codex_flow()
        prompts = [call.args[0] for call in module.notify_post.call_args_list]
        self.assertIn("for may", prompts[0])
        self.assertTrue(all("may" in prompt for prompt in prompts))

    def test_prompt_without_a_label_keeps_the_original_wording(self):
        module = load_script()
        module.LOGIN_LABEL = ""
        self.assertEqual(module._for_label(), "")
        module.LOGIN_LABEL = "august"
        self.assertEqual(module._for_label(), " for august")

    def test_existing_usable_credential_skips_network(self):
        module = load_script()
        resolve = mock.Mock(return_value={"api_key": "secret-existing-token"})
        module._codex_native = mock.Mock(
            return_value=("client-id", "https://issuer.example/oauth/token", mock.Mock(), resolve)
        )
        module._post_json_status = mock.Mock()

        self.assertEqual(module.run_openai_codex_flow(), 0)
        module._post_json_status.assert_not_called()

    def test_transient_refresh_error_does_not_replace_credentials(self):
        module = load_script()
        resolve = mock.Mock(
            side_effect=FakeAuthError("codex_refresh_failed", relogin_required=False)
        )
        module._codex_native = mock.Mock(
            return_value=("client-id", "https://issuer.example/oauth/token", mock.Mock(), resolve)
        )
        module._post_json_status = mock.Mock()

        self.assertEqual(module.run_openai_codex_flow(), 1)
        module._post_json_status.assert_not_called()


class GitHubFlowRegressionTests(unittest.TestCase):
    def test_authorized_token_is_persisted_without_being_logged(self):
        module = load_script()
        module.NOTIFY = "logs"
        module.CLIENT_ID = "client-id"
        module.TOKEN_ENV = "COPILOT_GITHUB_TOKEN"
        module._post_form = mock.Mock(
            side_effect=[
                {
                    "device_code": "secret-device-code",
                    "user_code": "ABCD-EFGH",
                    "verification_uri": "https://github.com/login/device",
                    "interval": 1,
                    "expires_in": 900,
                },
                {"access_token": "secret-github-token"},
            ]
        )
        module.notify_post = mock.Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            module.HERMES_HOME = Path(tmpdir)
            with mock.patch.object(module.time, "sleep"), contextlib.redirect_stdout(
                io.StringIO()
            ) as captured:
                result = module.run_github_device_flow()
            env_text = (Path(tmpdir) / ".env").read_text()

        self.assertEqual(result, 0)
        self.assertIn("COPILOT_GITHUB_TOKEN=secret-github-token", env_text)
        self.assertNotIn("secret-device-code", captured.getvalue())
        self.assertNotIn("secret-github-token", captured.getvalue())


if __name__ == "__main__":
    unittest.main()


class TelegramNotifyTests(unittest.TestCase):
    def _module(self, **attrs):
        module = load_script()
        module.NOTIFY = "telegram"
        module.TELEGRAM_BOT_TOKEN = "123456:SECRET-TOKEN"
        module.TELEGRAM_CHAT_ID = "-1001234567890"
        for key, value in attrs.items():
            setattr(module, key, value)
        return module

    def test_posts_message_to_the_telegram_chat(self):
        module = self._module()
        response = mock.MagicMock()
        response.__enter__.return_value.status = 200
        with mock.patch.object(
            module.urllib.request, "urlopen", return_value=response
        ) as urlopen, contextlib.redirect_stdout(io.StringIO()) as out:
            module.notify_post("Open https://example.test/device and enter ABCD-EFGH")
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://api.telegram.org/bot123456:SECRET-TOKEN/sendMessage",
        )
        body = module.json.loads(request.data)
        self.assertEqual(body["chat_id"], "-1001234567890")
        self.assertIn("ABCD-EFGH", body["text"])
        self.assertNotIn("SECRET-TOKEN", out.getvalue())

    def test_failure_is_logged_without_the_token_and_does_not_raise(self):
        module = self._module()
        error = module.urllib.error.URLError("boom SECRET-TOKEN")
        with mock.patch.object(
            module.urllib.request, "urlopen", side_effect=error
        ), contextlib.redirect_stdout(io.StringIO()) as out:
            module.notify_post("hello")
        self.assertIn("[telegram] post FAILED", out.getvalue())
        self.assertNotIn("SECRET-TOKEN", out.getvalue())

    def test_missing_credentials_skip_the_post(self):
        module = self._module(TELEGRAM_BOT_TOKEN="")
        with mock.patch.object(module.urllib.request, "urlopen") as urlopen:
            with contextlib.redirect_stdout(io.StringIO()):
                module.notify_post("hello")
        urlopen.assert_not_called()

    def test_notification_ready_requires_token_and_home_channel(self):
        self.assertTrue(self._module()._notification_ready())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertFalse(self._module(TELEGRAM_CHAT_ID="")._notification_ready())
        self.assertIn("TELEGRAM_BOT_TOKEN", out.getvalue())

    def test_logs_mode_never_posts(self):
        module = self._module(NOTIFY="logs")
        with mock.patch.object(module.urllib.request, "urlopen") as urlopen:
            module.notify_post("hello")
        urlopen.assert_not_called()


class ValuesDefaultsTests(unittest.TestCase):
    def test_copilot_validation_does_not_use_the_token_exchange_endpoint(self):
        # A valid token on a Copilot Free account got 403 from the exchange
        # endpoint, and the init container treats 403 as "invalid", so every
        # restart asked for a new login.
        # Plain text on purpose: the CI step has no PyYAML guarantee.
        text = (Path(__file__).parents[1] / "charts/hermes-agent/values.yaml").read_text()
        urls = re.findall(r"^\s+validateUrl: (\S+)\s*$", text, flags=re.M)
        self.assertEqual(len(urls), 1)
        url = urls[0]
        self.assertNotIn("copilot_internal", url)
        self.assertEqual(url, "https://api.github.com/user")


class TokenValidationTests(unittest.TestCase):
    def _module(self):
        module = load_script()
        module.VALIDATE_URL = "https://api.github.com/user"
        return module

    def test_revoked_token_is_invalid(self):
        module = self._module()
        error = module.urllib.error.HTTPError(module.VALIDATE_URL, 401, "Unauthorized", {}, None)
        with mock.patch.object(module.urllib.request, "urlopen", side_effect=error):
            self.assertFalse(module.token_is_valid("gho_revoked"))

    def test_live_token_is_valid(self):
        module = self._module()
        response = mock.MagicMock()
        response.__enter__.return_value.status = 200
        with mock.patch.object(module.urllib.request, "urlopen", return_value=response):
            self.assertTrue(module.token_is_valid("gho_live"))


class CheckNativeTests(unittest.TestCase):
    def test_passes_when_the_image_still_provides_the_helpers(self):
        module = load_script()
        module._codex_native = mock.Mock(return_value=("client", "url", mock.Mock(), mock.Mock()))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(module.check_native(), 0)
        self.assertIn("OK", out.getvalue())

    def test_fails_clearly_when_a_helper_is_gone(self):
        module = load_script()
        module._codex_native = mock.Mock(
            side_effect=ImportError("cannot import name '_save_codex_tokens' from 'hermes_cli.auth'")
        )
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(module.check_native(), 1)
        text = out.getvalue()
        self.assertIn("FAIL", text)
        self.assertIn("_save_codex_tokens", text)

    def test_main_runs_only_the_check_with_the_flag(self):
        module = load_script()
        module.check_native = mock.Mock(return_value=0)
        module.run_openai_codex_flow = mock.Mock()
        module.run_github_device_flow = mock.Mock()
        with mock.patch.object(module.sys, "argv", ["device_login.py", "--check-native"]):
            self.assertEqual(module.main(), 0)
        module.check_native.assert_called_once()
        module.run_openai_codex_flow.assert_not_called()
        module.run_github_device_flow.assert_not_called()
