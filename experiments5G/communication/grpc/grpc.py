from ..interface import CommunicationInterface
from concurrent import futures
import grpc
import time

from .grpc_pb2_grpc import LatencyExperimentsServicer, add_LatencyExperimentsServicer_to_server, LatencyExperimentsStub
from .grpc_pb2 import Request, Response


DEFAULT_PORT = 1234
GRPC_PACKET_SIZE_LIMIT = 4194304


def get_channel_options(packet_size):
    if packet_size < GRPC_PACKET_SIZE_LIMIT:
        return None
    else:
        p = packet_size * 10
        return [('grpc.max_send_message_length', p),
                ('grpc.max_receive_message_length', p),
                ('grpc.max_message_length', p)]


class GRPCChannelManager:
    def __init__(self):
        self.url = None
        self.channel = None

    def get_channel(self, host, port):
        url = f"{host}:{port}"
        if (self.channel is None) or (url != self.url):
            if self.channel is not None:
                try:
                    self.channel.close()
                except:
                    pass
                finally:
                    del self.channel
            self.channel = grpc.insecure_channel(
                url, options=get_channel_options(2*10**8))
        return self.channel

    def send(self, data: bytes, host, max_time: float, port):
        request = Request(data=data)
        channel = self.get_channel(host, port)
        stub = LatencyExperimentsStub(channel)
        t = time.time()
        response = stub.MyCall(request, timeout=max_time)
        duration = time.time() - t
        return duration, response.data


class grpcInterface(CommunicationInterface):
    @staticmethod
    def send(data: bytes, host, max_time: float, port=DEFAULT_PORT):
        return GRPCChannelManager().send(data, host, max_time, port)

    @staticmethod
    def listen(process_request_fn, port=DEFAULT_PORT):
        port = f"[::]:{port}"

        class MyServicer(LatencyExperimentsServicer):
            nonlocal process_request_fn

            def MyCall(self, request: Request, context):
                response_data = process_request_fn(
                    request.data, context.peer())
                return Response(data=response_data)

        server = grpc.server(futures.ThreadPoolExecutor(
            max_workers=10), options=get_channel_options(int(2*10**8)))
        add_LatencyExperimentsServicer_to_server(MyServicer(), server)
        server.add_insecure_port(port)
        print(f"starting gRPC server on port {port} ...")
        server.start()
        print("gRPC server started, waiting ...")
        server.wait_for_termination()
