"""Server REST api tests.
"""

import http.client
import json
import unittest

import flask
import flask_restplus as restplus
import mock

from treadmill import webutils
from treadmill.rest.api import server


class ServerTest(unittest.TestCase):
    """Test the logic corresponding to the /server namespace."""

    def setUp(self):
        """Initialize the app with the corresponding logic."""
        self.app = flask.Flask(__name__)
        self.app.testing = True

        api = restplus.Api(self.app)
        cors = webutils.cors(origin='*',
                             content_type='application/json',
                             credentials=False)
        self.impl = mock.Mock()

        server.init(api, cors, self.impl)
        self.client = self.app.test_client()

    def test_get_server_list(self):
        """Test getting a list of servers."""
        server_list = [
            {'cell': 'foo', 'traits': [], '_id': 'server1', 'data': []},
            {'cell': 'bar', 'traits': [], '_id': 'server2', 'data': []}
        ]
        self.impl.list.return_value = server_list

        resp = self.client.get('/server/')

        self.assertEqual(
            json.loads((b''.join(resp.response)).decode()),
            server_list
        )
        self.assertEqual(resp.status_code, http.client.OK)
        self.impl.list.assert_called_with(None, None)

        resp = self.client.get('/server/?cell=foo')
        self.assertEqual(resp.status_code, http.client.OK)
        self.impl.list.assert_called_with('foo', None)

        resp = self.client.get('/server/?partition=baz')
        self.assertEqual(resp.status_code, http.client.OK)
        self.impl.list.assert_called_with(None, 'baz')

        resp = self.client.get('/server/?cell=foo&partition=baz')
        self.assertEqual(resp.status_code, http.client.OK)
        self.impl.list.assert_called_with('foo', 'baz')


if __name__ == '__main__':
    unittest.main()
