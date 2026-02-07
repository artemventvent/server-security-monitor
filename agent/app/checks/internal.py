import subprocess
from .base import BaseCheck

class SSHRootLoginCheck(BaseCheck):
    id = "ssh_root_login"
    title = "SSH root login disabled"
    severity = "high"

    def run(self):
        try:
            with open("/etc/ssh/sshd_config") as f:
                content = f.read()

            if "PermitRootLogin yes" in content:
                return {
                    "status": "fail",
                    "evidence": "PermitRootLogin yes",
                    "recommendation": "Set PermitRootLogin no in /etc/ssh/sshd_config"
                }
            else:
                return {
                    "status": "pass",
                    "evidence": "Root login disabled"
                }
        except Exception as e:
            return {
                "status": "error",
                "evidence": str(e)
            }


class UFWCheck(BaseCheck):
    id = "ufw_enabled"
    title = "Firewall enabled"
    severity = "medium"

    def run(self):
        try:
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            if "active" in result.stdout.lower():
                return {
                    "status": "pass",
                    "evidence": "ufw active"
                }
            else:
                return {
                    "status": "fail",
                    "evidence": result.stdout,
                    "recommendation": "Enable firewall: ufw enable"
                }
        except Exception as e:
            return {
                "status": "error",
                "evidence": str(e)
            }