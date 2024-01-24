import unittest
from experiments5G.communication import CommunicationInterface
import multiprocessing
import time

def generic_test(interface: CommunicationInterface):
    request_str = "Hello, this is the client. I want to know something. Give me a response."
    response_str = "Hello, this is the server. Thanks for your request. The answer is 42. Over."
    
    def server_fn(request: bytes, client: str) -> bytes:
        assert request.decode() == request_str
        return response_str.encode()

    p = multiprocessing.Process(target=interface.listen, args=(server_fn,))
    try:
        p.start()
        time.sleep(2) # NOTE: THIS IS VERY, VERY BAD; STARTING THE SERVERS MIGHT TAKE LONGER THAN 2 SECONDS
        duration, response = interface.send(request_str.encode(), "localhost", 2.0)
        assert response.decode() == response_str
    finally:
        p.terminate()

class InterfaceTest(unittest.TestCase):
    def test_zmq(self):
        from experiments5G.communication.zmq import zmqInterface
        generic_test(zmqInterface)

    def test_rest(self):
        from experiments5G.communication.rest import RESTInterface
        import asyncio
        from tornado.platform.asyncio import AnyThreadEventLoopPolicy
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
        generic_test(RESTInterface)

    def test_mqtt(self):
        import asyncio
        from tornado.platform.asyncio import AnyThreadEventLoopPolicy
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
        from experiments5G.communication.mqtt import MQTTInterface
        generic_test(MQTTInterface)

    def test_grpc(self):
        from experiments5G.communication.grpc import grpcInterface
        generic_test(grpcInterface)

if __name__ == '__main__':
    unittest.main()
