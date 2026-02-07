from agent.app.checks.internal import SSHRootLoginCheck, UFWCheck

CHECKS = [
    SSHRootLoginCheck(),
    UFWCheck()
]

def collect():
    results = []

    for check in CHECKS:
        data = check.run()
        result = {
            "check_id": check.id,
            "title": check.title,
            "severity": check.severity,
            **data
        }
        results.append(result)

    return results