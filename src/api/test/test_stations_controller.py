# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from api.models.radio_station import RadioStation  # noqa: E501
from api.models.search_result import SearchResult  # noqa: E501
from api.test import BaseTestCase


class TestStationsController(BaseTestCase):
    """StationsController integration test stubs"""

    def test_get_station_by_country_code_and_station_id(self):
        response = self.client.open(
            '/api/stations/{namespace}/{slug}'.format(namespace='fr', slug='radiomeuh'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))



if __name__ == '__main__':
    import unittest
    unittest.main()
