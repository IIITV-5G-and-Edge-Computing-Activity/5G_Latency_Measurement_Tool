from experiments5G.commons.packet_logger import data_to_bytes, bytes_to_logitem
import unittest

class LoggerTest(unittest.TestCase):
    def test_1(self):
        pos = (123.2, 2323.2222222323)
        n_bytes = 333333
        cache = {"a": 123, "b": "hello world"}
        request_data = data_to_bytes(n_bytes, pos, cache)
        self.assertEqual(n_bytes, len(request_data))
        response_data = bytes(True)
        logitem = bytes_to_logitem(request_data, response_data)
        self.assertEqual(logitem.y, pos[0])
        self.assertEqual(logitem.x, pos[1])
        self.assertEqual(logitem.cache, cache)
        print(logitem.cache)
        self.assertEqual(logitem.size, n_bytes)

if __name__ == '__main__':
    unittest.main()
