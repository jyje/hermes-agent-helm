from pathlib import Path
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).parents[1]
CHART = ROOT / "charts/hermes-agent"


@unittest.skipUnless(shutil.which("helm"), "helm is required for render checks")
class TelegramWebhookExampleTests(unittest.TestCase):
    def test_native_listener_service_route_and_readiness_agree(self):
        for controller, kind in (("deployment", "Deployment"), ("statefulset", "StatefulSet")):
            with self.subTest(controller=controller):
                rendered = subprocess.check_output([
                    "helm", "template", "webhook", str(CHART),
                    "-f", str(CHART / "values-telegram-webhook.yaml"),
                    "--set", f"controller.type={controller}",
                ], text=True)
                docs = [d for d in yaml.safe_load_all(rendered) if d]
                service = next(d for d in docs if d["kind"] == "Service"
                               and d["spec"].get("clusterIP") != "None")
                ingress = next(d for d in docs if d["kind"] == "Ingress")
                workload = next(d for d in docs if d["kind"] == kind)
                container = workload["spec"]["template"]["spec"]["containers"][0]
                env = {e["name"]: e.get("value") for e in container["env"]}
                listener_port = int(env["TELEGRAM_WEBHOOK_PORT"])
                public_url = urlsplit(env["TELEGRAM_WEBHOOK_URL"])
                self.assertEqual(public_url.scheme, "https")
                self.assertEqual(len(service["spec"]["ports"]), 1)
                port = service["spec"]["ports"][0]
                self.assertEqual(port["targetPort"], listener_port)
                self.assertEqual(container["readinessProbe"]["tcpSocket"]["port"], listener_port)
                rule = ingress["spec"]["rules"][0]
                path = rule["http"]["paths"][0]
                self.assertEqual(rule["host"], public_url.hostname)
                self.assertEqual(path["path"], public_url.path)
                self.assertEqual(path["backend"]["service"]["name"], service["metadata"]["name"])
                self.assertEqual(path["backend"]["service"]["port"]["number"], port["port"])
                self.assertIn(public_url.hostname, ingress["spec"]["tls"][0]["hosts"])
                self.assertNotIn("TELEGRAM_WEBHOOK_SECRET", env)
                self.assertTrue(any("secretRef" in ref for ref in container["envFrom"]))
                self.assertFalse({"HERMES_DASHBOARD", "WEBHOOK_ENABLED", "API_SERVER_ENABLED"} & env.keys())
                self.assertNotIn("command", container)


if __name__ == "__main__":
    unittest.main()
