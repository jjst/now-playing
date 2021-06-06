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
        """Test case for get_station_by_country_code_and_station_id

        Find pet by ID
        """
        response = self.client.open(
            '/api/stations/{countryCode}/{stationId}'.format(countryCode='countryCode_example', stationId='stationId_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search(self):
        """Test case for search

        Finds a station by name
        """
        query_string = [('query', 'query_example')]
        response = self.client.open(
            '/api/search',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
