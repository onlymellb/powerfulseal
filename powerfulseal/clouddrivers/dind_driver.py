import logging
import docker
from . import AbstractDriver
from ..node import Node, NodeState


def create_docker_cli_from_url(base_url=None):
    """ Creates a new docker client """
    return docker.Client(base_url=base_url)

def get_all_ips(server):
    """
        Digs out the IPs from the server['NetworkSettings']['Networks'] field
        of a dind server.
    """
    output = []
    networks = server['NetworkSettings']['Networks']
    for key, value in networks.items():
        if value['IPAMConfig'] is None:
            # using docker's default network causes this field to be None
            # so be sure to use a custom network
            continue
        output.append(value['IPAMConfig']['IPv4Address'])
    return output

MAPPING_STATES_STATUS = {
    "RUNNING": NodeState.UP,
    "EXITED": NodeState.DOWN,
}
def server_status_to_state(status):
    return MAPPING_STATES_STATUS.get(status.upper(), NodeState.UNKNOWN)

def create_node_from_server(server):
    """ Translate DinD server representation into a Node object.
    """
    return Node(
        id=server['Id'],
        ip=get_all_ips(server)[-1],
        az="china",
        name=server['Names'][0].split('/')[-1],
        state=server_status_to_state(server['State']),
    )


class DindDriver(AbstractDriver):
    """
        Concrete implementation of the dind cloud driver.
    """

    def __init__(self, base_url=None, filters=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.filters = filters
        self.cli = create_docker_cli_from_url(base_url)
        self.remote_servers = []

    def sync(self):
        """ Downloads a fresh set of nodes form the API.
        """
        self.logger.info("Synchronizing dind nodes")
        self.remote_servers = self.cli.containers(filters=self.filters, all=True)
        print(len(self.remote_servers))
        self.logger.info("Fetched %s dind servers" % len(self.remote_servers))

    def get_by_ip(self, ip):
        """ Retreive an instance of Node by its IP.
        """
        for server in self.remote_servers:
            addresses = get_all_ips(server)
            if not addresses:
                self.logger.warning("No addresses found: %s", server)
            else:
                for addr in addresses:
                    if addr == ip:
                        return create_node_from_server(server)
        return None

    def stop(self, node):
        """ Stop a Node.
        """
        self.cli.stop(node.id)

    def start(self, node):
        """ Start a Node.
        """
        self.cli.start(node.id)

    def delete(self, node):
        """ Delete a Node permanently.
        """
        self.cli.remove_constainer(node.id)
