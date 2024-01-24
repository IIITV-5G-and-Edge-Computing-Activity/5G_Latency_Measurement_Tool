from .interface import CommunicationInterface
import asyncio
import mqttools
import threading
import time

# mqttools: https://github.com/eerimoq/mqttools


DEFAULT_PORT = 1883


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def start_broker(host, port):
    broker = mqttools.Broker((host, port))
    asyncio.run(broker.serve_forever())


REQUEST_TOPIC = "/requests"
RESPONSE_TOPIC = "/responses"


class MQTTInterface(CommunicationInterface):
    @staticmethod
    def send(data: bytes, host, max_time: float, port=DEFAULT_PORT):
        async def publisher(_data):
            async with mqttools.Client(host, port, connect_delays=[], response_timeout=max_time) as client:
                await client.subscribe(RESPONSE_TOPIC)
                message = mqttools.Message(topic=REQUEST_TOPIC, message=_data, response_topic=RESPONSE_TOPIC)
                t = time.time()
                client.publish(message)
                response = await client.messages.get()
                assert response is not None
                response_data = response.message
                # client.messages.task_done()
                duration = time.time() - t
            return duration, response_data
        return asyncio.run(publisher(data))

    @staticmethod
    def listen(process_request_fn, port=DEFAULT_PORT):
        host = "localhost"

        if not is_port_in_use(port):
            threading.Thread(target=start_broker, args=(None, port)).start()
            print(f"MQTT Broker started on port {port}")
            time.sleep(1)
        else:
            print(
                f"MQTT: Port {port} is in use; Hopefully the MQTT broker is running there.")

        async def subscriber():
            nonlocal process_request_fn, port
            async with mqttools.Client(host, port) as client:
                await client.subscribe(REQUEST_TOPIC)
                while True:
                    message = await client.messages.get()
                    if message is None:
                        raise Exception('Broker connection lost!')
                    # response_data = process_request_fn(message.message, None)
                    response_message = mqttools.Message(topic=message.response_topic, message=process_request_fn(message.message, None))
                    client.publish(response_message)
                    client.messages.task_done()
        print(f"MQTT subscriber registered on port {port}")
        asyncio.run(subscriber())
