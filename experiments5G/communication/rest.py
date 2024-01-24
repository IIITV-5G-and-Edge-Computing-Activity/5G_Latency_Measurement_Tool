from .interface import CommunicationInterface
import requests
import tornado.web
import tornado.ioloop
import time

DEFAULT_PORT = 8080

class RESTInterface(CommunicationInterface):
    @staticmethod
    def send(data: bytes, host, max_time: float, port=DEFAULT_PORT):
        url = f"http://{host}:{port}"
        t = time.time()
        response = requests.post(url,
                                data=data,
                                timeout=max_time)
        delta_t = time.time() - t
        status_code = int(response.status_code)
        if (status_code != 201) and (status_code != 200):
            raise Exception(
                f"REST possibly failed: Received HTTP status code {status_code} (expected 200 or 201)")
        return delta_t, response.content

    @staticmethod
    def listen(process_request_fn, port=DEFAULT_PORT):
        port = port if port is not None else DEFAULT_PORT

        class MainHandler(tornado.web.RequestHandler):
            nonlocal process_request_fn
            # TODO: HTTP-Header includes a datetime, maybe use this for more accuracy?

            def get(self):
                # GET request
                self.write("12345678")

            def post(self):
                data = self.request.body
                response = process_request_fn(data, self.request.remote_ip)
                # if response is not None:
                self.write(response)
        print(f"Starting REST server on port {port}")
        app = tornado.web.Application([
            (r"/", MainHandler),
        ])
        app.listen(port)
        print("REST server started, listening ...")
        tornado.ioloop.IOLoop.instance().start()
