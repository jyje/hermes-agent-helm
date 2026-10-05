import asyncio
import contextlib
import importlib.util
import io
import json
import logging
import os
import unittest
from pathlib import Path
from unittest import mock


HOOK = Path(__file__).parents[1] / "charts/hermes-agent/files/hooks/ready_notify.py"


def load_hook():
    spec = importlib.util.spec_from_file_location("ready_notify_under_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def accepted_response():
    response = mock.MagicMock()
    response.__enter__.return_value.status = 200
    return response


class BuildMessageTests(unittest.TestCase):
    def test_names_the_release_and_the_platforms(self):
        module = load_hook()
        text = module.build_message("may", ["telegram"])
        self.assertIn("may is ready", text)
        self.assertIn("telegram", text)

    def test_works_without_a_label_or_platforms(self):
        module = load_hook()
        self.assertTrue(module.build_message("", []).startswith("The agent is ready"))


class SendTests(unittest.TestCase):
    def test_telegram_posts_to_the_home_channel(self):
        module = load_hook()
        env = {"TELEGRAM_BOT_TOKEN": "123:SECRET", "TELEGRAM_HOME_CHANNEL": "-100"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            module.urllib.request, "urlopen", return_value=accepted_response()
        ) as urlopen:
            self.assertTrue(module.send("telegram", "may is ready"))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/bot123:SECRET/sendMessage")
        body = json.loads(request.data)
        self.assertEqual(body["chat_id"], "-100")
        self.assertEqual(body["text"], "may is ready")

    def test_discord_posts_with_a_bot_authorization_header(self):
        module = load_hook()
        env = {"DISCORD_BOT_TOKEN": "tok", "DISCORD_HOME_CHANNEL": "42"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            module.urllib.request, "urlopen", return_value=accepted_response()
        ) as urlopen:
            self.assertTrue(module.send("discord", "hello"))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://discord.com/api/v10/channels/42/messages")
        self.assertEqual(request.get_header("Authorization"), "Bot tok")
        self.assertEqual(json.loads(request.data), {"content": "hello"})

    def test_missing_credentials_skip_the_request(self):
        module = load_hook()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            module.urllib.request, "urlopen"
        ) as urlopen:
            self.assertFalse(module.send("telegram", "hello"))
            self.assertFalse(module.send("discord", "hello"))
        urlopen.assert_not_called()

    def test_failure_never_logs_the_token(self):
        module = load_hook()
        env = {"TELEGRAM_BOT_TOKEN": "123:SECRET", "TELEGRAM_HOME_CHANNEL": "-100"}
        error = module.urllib.error.URLError("boom 123:SECRET")
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        module.logger.addHandler(handler)
        try:
            with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
                module.urllib.request, "urlopen", side_effect=error
            ):
                self.assertFalse(module.send("telegram", "hello"))
        finally:
            module.logger.removeHandler(handler)
        self.assertIn("FAILED", stream.getvalue())
        self.assertNotIn("SECRET", stream.getvalue())


class HandleTests(unittest.TestCase):
    def test_does_nothing_without_a_configured_channel(self):
        module = load_hook()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            module, "send"
        ) as send:
            asyncio.run(module.handle("gateway:startup", {"platforms": ["telegram"]}))
        send.assert_not_called()

    def test_posts_the_label_and_active_platforms(self):
        module = load_hook()
        env = {"READY_NOTIFY": "telegram", "READY_NOTIFY_LABEL": "august"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            module, "send", return_value=True
        ) as send:
            asyncio.run(module.handle("gateway:startup", {"platforms": ["telegram", "api_server"]}))
        channel, text = send.call_args.args
        self.assertEqual(channel, "telegram")
        self.assertIn("august is ready", text)
        self.assertIn("telegram, api_server", text)

    def test_tolerates_a_missing_context(self):
        module = load_hook()
        env = {"READY_NOTIFY": "discord"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            module, "send", return_value=True
        ) as send:
            asyncio.run(module.handle("gateway:startup", None))
        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
