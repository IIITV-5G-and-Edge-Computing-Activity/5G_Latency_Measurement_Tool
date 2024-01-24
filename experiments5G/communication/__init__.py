from .mqtt import MQTTInterface
from .rest import RESTInterface
from .zmq import zmqInterface
from .grpc.grpc import grpcInterface
from .interface import CommunicationInterface
from typing import Dict

# import 
INTERFACES: Dict[str, CommunicationInterface] = {
    "MQTT": MQTTInterface,
    "GRPC": grpcInterface,
    "REST": RESTInterface,
    "ZMQ": zmqInterface
}
