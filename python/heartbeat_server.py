from concurrent import futures
import logging
import os
import time

import click
import grpc

import heartbeat_pb2
import heartbeat_pb2_grpc

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class HeartbeatServicer(heartbeat_pb2_grpc.HeartbeatServicer):

    def __init__(self):
        self.clients = {}
        self._next_client_id = 0
        log.info("HeartbeatServicer created")

    def Join(self, request, context):
        log.info("Received join request. Assigning id {}".format(
            self._next_client_id))
        resp = heartbeat_pb2.JoinResponse(ok=True, id=self._next_client_id)
        self._next_client_id += 1
        return resp

    def SendHeartbeat(self, request, context):
        log.info("Received heartbeat from {}".format(request.id))
        return heartbeat_pb2.HeartbeatResponse(token=request.token)
    
    def serve(self, address):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        heartbeat_pb2_grpc.add_HeartbeatServicer()

@click.command()
@click.option("--cpus", default=1,
              help="Number of cpus to use in handling heartbeat requests.")
@click.option("--address", default="localhost:1024",
              help="Address:port for server to bind to.")
def main(cpus, address):
    server = grpc.server(futures.ThreadPoolExecutor(cpus))
    heartbeat_pb2_grpc.add_HeartbeatServicer_to_server(HeartbeatServicer(),
                                                       server)
    server.add_insecure_port(address)
    log.info("Starting server")
    server.start()
    log.info("Listening on {}".format(address))
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        log.info("Shutting down...")

if __name__ == "__main__":
    main()
