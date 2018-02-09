class DockerExecutor(object):
    """
        Executes commands on dind Node instances via docker exec
    """

    def __init__(self, dockerClient, nodes=None):
        self.nodes = nodes or []
        self.cli = dockerClient

    def execute(self, cmd, nodes=None, debug=False):
        nodes = nodes or self.nodes
        results = dict()
        for node in nodes:
            cmd=cmd.lstrip('sudo').strip()
            exec_obj = self.cli.exec_create(node.id, cmd)
            print("Executing '%s' on %s" % (cmd, node.name))
            try:
                output = self.cli.exec_start(exec_obj).decode().strip()
                if 'exec failed' in output:
                    results[node.ip] = {
                        "ret_code": 1,
                        "error": output,
                    }
                else:
                    results[node.ip] = {
                        "ret_code": 0,
                        "stdout": output,
                        "stderr": "",
                    }
            except Exception as e:
                results[node.ip] = {
                    "ret_code": 1,
                    "error": str(e),
                }
        return results
