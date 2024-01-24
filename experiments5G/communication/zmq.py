from .interface import CommunicationInterface
import zmq
import time

SUCCESS = True.to_bytes(1, "big")
FAILURE = False.to_bytes(1, "big")
DEFAULT_PORT = 5555

class zmqInterface(CommunicationInterface):
    @staticmethod
    def send(data: bytes, host, max_time: float, port=DEFAULT_PORT):
        duration = None
        response_data = None
        context = None
        socket = None
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.setsockopt(zmq.LINGER, 0)
            socket.setsockopt(zmq.SNDTIMEO, int(max_time * 1000))
            socket.setsockopt(zmq.RCVTIMEO, int(max_time * 1000))
            # socket.setsockopt(zmq.CONNECT_TIMEOUT, int(max_time * 1000))
            socket.setsockopt(zmq.RECONNECT_IVL, -1)
            socket.connect(f"tcp://{host}:{port}")
            t = time.time()
            socket.send(data)
            response_data = socket.recv()
            duration = time.time() - t
        finally:
            if socket is not None:
                socket.close()
            if context is not None:
                context.term()
            del socket, context
        return duration, response_data

    @staticmethod
    def listen(process_request_fn, port=DEFAULT_PORT):
        print(f"Starting zmq server on port {port}")
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{port}")
        print(f"zmq server started, entering infinite receive loop...")
        while True:
            message = socket.recv()
            response_data=process_request_fn(message, "unknown")
            response_data = SUCCESS if response_data is None else response_data
            socket.send(response_data)
            # Unfortunately, there is no way to get peer IP
