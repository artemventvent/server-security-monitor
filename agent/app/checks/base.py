class BaseCheck:
    id = "base"
    title = "base check"
    severity = "low"

    def run(self):
        raise NotImplementedError("run() must be implemented")