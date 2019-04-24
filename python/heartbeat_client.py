import random
import logging
from multiprocessing import Pool
import os
import time

import click
import grpc

import heartbeat_pb2
import heartbeat_pb2_grpc

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, interval):
        self.channel = None
        self.stub = None
        self.id = -1
        self.interval = interval

    def connect(self, address):
        self.channel = grpc.insecure_channel(address)
        print("created channel: {}".format(self.channel))
        self.stub = heartbeat_pb2_grpc.HeartbeatStub(self.channel)
        print("created stub: {}".format(self.stub))
        req = heartbeat_pb2.JoinRequest()
        print(req)
        log.info("Attempting to join heartbeat service at {}".format(address))
        join_response = self.stub.Join(req)
        log.info("Response received: {}".format(join_response))
        if join_response.ok:
            self.id = join_response.id
            log.info("Connected with id {}".format(self.id))
        else:
            log.error("Failed to join heartbeat server. Exiting...")
            os.exit(1)

    def serve(self):
        while True:
            time.sleep(self.interval)

            token = random.randint(0, 2<<31)
            msg = heartbeat_pb2.HeartbeatMessage(id=self.id, token=token)
            resp = self.stub.SendHeartbeat(msg)
            if resp.token != token:
                log.error(
                    "Heartbeat response failure: expected {} got {}".format(
                        token, resp.token))
            else:
                log.info("[{}] heartbeat acknowledged".format(self.id))


@click.command()
@click.option("--interval", default=1,
              help="Interval in seconds between heartbeats.")
@click.option("--address", default="localhost:1024",
              help="address:port for heartbeat server.")
@click.option("--cpus", default=1,
              help="Number of cpus to use while running clients.")
def main(interval, address, cpus):
    c = Client(interval)
    c.connect(address)
    log.info("Connected")
    c.serve()

if __name__ == "__main__":
    main()
