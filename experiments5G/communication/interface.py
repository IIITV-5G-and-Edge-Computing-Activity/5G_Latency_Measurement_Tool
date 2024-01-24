from typing import Callable, Any, Tuple, Optional

class CommunicationInterface:
    @staticmethod
    def send(data: bytes, host, max_time: float, port=None) -> Tuple[float, bytes]:
        """
        data: the bytes that are going to be sent
        host: the server IP
        max_time: timeout
        port: If not supplied, the default port for this communication library will be used
        
        Returns tuple (time taken, response bytes)
        """
        raise NotImplementedError()

    @staticmethod
    def listen(process_request_fn: Callable[[bytes, Any], bytes], port=None) -> Tuple[float, bytes]:
        """
        process_data_fn: client request bytes, client address -> response bytes
        port: Use default port for the library if not given

        Returns tuple (time taken, response bytes)
        """
        raise NotImplementedError()
