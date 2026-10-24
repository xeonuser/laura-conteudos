import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from smartbox.server import create_server


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.server = create_server(port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def call(self, path, body=None, token=None, origin=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        if origin:
            headers['Origin'] = origin
        req = Request(self.base+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        with urlopen(req) as r:
            return json.load(r)

    def test_catalog_and_health(self):
        self.assertEqual(self.call('/api/health')['adapter'], 'simulation')
        self.assertEqual(len(self.call('/api/catalog')), 3)
        with urlopen(self.base) as r:
            self.assertIn(b'Aurora TV', r.read())

    def test_pair_command_and_tv_isolation(self):
        with self.assertRaises(HTTPError) as e:
            self.call('/api/events')
        self.assertEqual(e.exception.code, 401)
        token = self.call('/api/pair', {'code': self.server.runtime.code})['token']
        self.call('/api/command', {'command': 'search', 'text': 'Sintel'}, token)
        events = self.call('/api/events', token=self.server.runtime.tv_token)['events']
        self.assertEqual(events[0]['text'], 'Sintel')
        with self.assertRaises(HTTPError):
            self.call('/api/events', token=token)
        self.call('/api/now', {'title': 'Sintel'}, self.server.runtime.tv_token)
        self.assertEqual(self.call('/api/now', token=token)['title'], 'Sintel')

    def test_invalid_expired_rate_limit_and_origin(self):
        for _ in range(5):
            with self.assertRaises(HTTPError) as e:
                self.call('/api/pair', {'code': 'wrong'})
            self.assertEqual(e.exception.code, 403)
        with self.assertRaises(HTTPError) as e:
            self.call('/api/pair', {'code': self.server.runtime.code})
        self.assertEqual(e.exception.code, 429)
        with self.assertRaises(HTTPError) as e:
            self.call('/api/pair', {'code': '123456'}, origin='http://evil.example')
        self.assertEqual(e.exception.code, 403)

    def test_code_single_use_and_invalid_command(self):
        code = self.server.runtime.code
        token = self.call('/api/pair', {'code': code})['token']
        with self.assertRaises(HTTPError):
            self.call('/api/pair', {'code': code})
        with self.assertRaises(HTTPError) as e:
            self.call('/api/command', {'command': 'shutdown'}, token)
        self.assertEqual(e.exception.code, 400)


if __name__ == '__main__':
    unittest.main()
