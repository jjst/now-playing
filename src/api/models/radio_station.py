# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from api.models.base_model_ import Model
from api.models.stream import Stream  # noqa: F401,E501
from api import util


class RadioStation(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, id: str=None, namespace: str=None, slug: str=None, name: str=None, favicon: str=None, country_code: str=None, streams: List[Stream]=None):  # noqa: E501
        """RadioStation - a model defined in Swagger

        :param id: The id of this RadioStation.  # noqa: E501
        :type id: str
        :param namespace: The namespace of this RadioStation.  # noqa: E501
        :type namespace: str
        :param slug: The slug of this RadioStation.  # noqa: E501
        :type slug: str
        :param name: The name of this RadioStation.  # noqa: E501
        :type name: str
        :param favicon: The favicon of this RadioStation.  # noqa: E501
        :type favicon: str
        :param country_code: The country_code of this RadioStation.  # noqa: E501
        :type country_code: str
        :param streams: The streams of this RadioStation.  # noqa: E501
        :type streams: List[Stream]
        """
        self.swagger_types = {
            'id': str,
            'namespace': str,
            'slug': str,
            'name': str,
            'favicon': str,
            'country_code': str,
            'streams': List[Stream]
        }

        self.attribute_map = {
            'id': 'id',
            'namespace': 'namespace',
            'slug': 'slug',
            'name': 'name',
            'favicon': 'favicon',
            'country_code': 'country_code',
            'streams': 'streams'
        }
        self._id = id
        self._namespace = namespace
        self._slug = slug
        self._name = name
        self._favicon = favicon
        self._country_code = country_code
        self._streams = streams

    @classmethod
    def from_dict(cls, dikt) -> 'RadioStation':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The RadioStation of this RadioStation.  # noqa: E501
        :rtype: RadioStation
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this RadioStation.


        :return: The id of this RadioStation.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this RadioStation.


        :param id: The id of this RadioStation.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def namespace(self) -> str:
        """Gets the namespace of this RadioStation.


        :return: The namespace of this RadioStation.
        :rtype: str
        """
        return self._namespace

    @namespace.setter
    def namespace(self, namespace: str):
        """Sets the namespace of this RadioStation.


        :param namespace: The namespace of this RadioStation.
        :type namespace: str
        """
        if namespace is None:
            raise ValueError("Invalid value for `namespace`, must not be `None`")  # noqa: E501

        self._namespace = namespace

    @property
    def slug(self) -> str:
        """Gets the slug of this RadioStation.


        :return: The slug of this RadioStation.
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug: str):
        """Sets the slug of this RadioStation.


        :param slug: The slug of this RadioStation.
        :type slug: str
        """
        if slug is None:
            raise ValueError("Invalid value for `slug`, must not be `None`")  # noqa: E501

        self._slug = slug

    @property
    def name(self) -> str:
        """Gets the name of this RadioStation.


        :return: The name of this RadioStation.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this RadioStation.


        :param name: The name of this RadioStation.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def favicon(self) -> str:
        """Gets the favicon of this RadioStation.


        :return: The favicon of this RadioStation.
        :rtype: str
        """
        return self._favicon

    @favicon.setter
    def favicon(self, favicon: str):
        """Sets the favicon of this RadioStation.


        :param favicon: The favicon of this RadioStation.
        :type favicon: str
        """

        self._favicon = favicon

    @property
    def country_code(self) -> str:
        """Gets the country_code of this RadioStation.


        :return: The country_code of this RadioStation.
        :rtype: str
        """
        return self._country_code

    @country_code.setter
    def country_code(self, country_code: str):
        """Sets the country_code of this RadioStation.


        :param country_code: The country_code of this RadioStation.
        :type country_code: str
        """

        self._country_code = country_code

    @property
    def streams(self) -> List[Stream]:
        """Gets the streams of this RadioStation.


        :return: The streams of this RadioStation.
        :rtype: List[Stream]
        """
        return self._streams

    @streams.setter
    def streams(self, streams: List[Stream]):
        """Sets the streams of this RadioStation.


        :param streams: The streams of this RadioStation.
        :type streams: List[Stream]
        """

        self._streams = streams
