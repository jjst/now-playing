# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from api.models.base_model_ import Model
from api import util


class Stream(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, url: str=None, quality: str=None, bitrate_kbps: int=None):  # noqa: E501
        """Stream - a model defined in Swagger

        :param url: The url of this Stream.  # noqa: E501
        :type url: str
        :param quality: The quality of this Stream.  # noqa: E501
        :type quality: str
        :param bitrate_kbps: The bitrate_kbps of this Stream.  # noqa: E501
        :type bitrate_kbps: int
        """
        self.swagger_types = {
            'url': str,
            'quality': str,
            'bitrate_kbps': int
        }

        self.attribute_map = {
            'url': 'url',
            'quality': 'quality',
            'bitrate_kbps': 'bitrate_kbps'
        }

        self._url = url
        self._quality = quality
        self._bitrate_kbps = bitrate_kbps

    @classmethod
    def from_dict(cls, dikt) -> 'Stream':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Stream of this Stream.  # noqa: E501
        :rtype: Stream
        """
        return util.deserialize_model(dikt, cls)

    @property
    def url(self) -> str:
        """Gets the url of this Stream.


        :return: The url of this Stream.
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url: str):
        """Sets the url of this Stream.


        :param url: The url of this Stream.
        :type url: str
        """
        if url is None:
            raise ValueError("Invalid value for `url`, must not be `None`")  # noqa: E501

        self._url = url

    @property
    def quality(self) -> str:
        """Gets the quality of this Stream.


        :return: The quality of this Stream.
        :rtype: str
        """
        return self._quality

    @quality.setter
    def quality(self, quality: str):
        """Sets the quality of this Stream.


        :param quality: The quality of this Stream.
        :type quality: str
        """

        self._quality = quality

    @property
    def bitrate_kbps(self) -> int:
        """Gets the bitrate_kbps of this Stream.


        :return: The bitrate_kbps of this Stream.
        :rtype: int
        """
        return self._bitrate_kbps

    @bitrate_kbps.setter
    def bitrate_kbps(self, bitrate_kbps: int):
        """Sets the bitrate_kbps of this Stream.


        :param bitrate_kbps: The bitrate_kbps of this Stream.
        :type bitrate_kbps: int
        """

        self._bitrate_kbps = bitrate_kbps