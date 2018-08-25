"""Tests for http"""

___license___      = "MIT"
___dependencies___ = ["upip:unittest", "http", "wifi"]

import unittest
from http import *
import wifi

class TestHttp(unittest.TestCase):

    def setUpClass(self):
        wifi.connect()

    def test_get_with_https(self):
        with get("https://httpbin.org/get") as response:
            self.assertEqual(response.status, 200)
            print(response.text)

    def test_get(self):
        with get("http://httpbin.org/get", params={"foo": "bar"}, headers={"accept": "application/json"}) as response:
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertEqual(response.status, 200)
            content = response.json()
            self.assertEqual(content["headers"]["Accept"], "application/json")
            self.assertEqual(content["args"], {"foo":"bar"})

    def test_post_form(self):
        with post("http://httpbin.org/post", data={"foo": "bar"}).raise_for_status() as response:
            content = response.json()
            self.assertEqual(content["headers"]["Content-Type"], "application/x-www-form-urlencoded")
            self.assertEqual(content["form"], {"foo":"bar"})

    def test_post_string(self):
        with post("http://httpbin.org/post", data="foobar").raise_for_status() as response:
            content = response.json()
            self.assertEqual(content["headers"]["Content-Type"], "text/plain; charset=UTF-8")
            self.assertEqual(content["data"], "foobar")

    def test_post_json(self):
        with post("http://httpbin.org/post", json={"foo":"bar"}).raise_for_status() as response:
            content = response.json()
            self.assertEqual(content["headers"]["Content-Type"], "application/json")
            self.assertEqual(content["json"], {"foo":"bar"})


if __name__ == '__main__':
    unittest.main()
