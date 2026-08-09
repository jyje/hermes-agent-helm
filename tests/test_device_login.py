import contextlib
import importlib.util
import io
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
        module.discord_post = mock.Mock()

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
        module.discord_post = mock.Mock()

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
