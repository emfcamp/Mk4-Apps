"""Tests for http"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "websockets", "wifi"]

import unittest
from websockets import connect
import wifi

class TestWebsockets(unittest.TestCase):

    def setUpClass(self):
        wifi.connect()

    def test_echo_service(self):
        ws = connect("ws://echo.websocket.org")
        self.assertTrue(ws.open)
        ws.send("Hello from TiLDA")
        response = ws.recv()
        self.assertEqual(response, "Hello from TiLDA")

if __name__ == '__main__':
    unittest.main()
