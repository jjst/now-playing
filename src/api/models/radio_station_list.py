# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from api.models.base_model_ import Model
from api.models.radio_station import RadioStation  # noqa: F401,E501
from api import util


class RadioStationList(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, items: List[RadioStation]=None):  # noqa: E501
        """RadioStationList - a model defined in Swagger

        :param items: The items of this RadioStationList.  # noqa: E501
        :type items: List[RadioStation]
        """
        self.swagger_types = {
            'items': List[RadioStation]
        }

        self.attribute_map = {
            'items': 'items'
        }
        self._items = items

    @classmethod
    def from_dict(cls, dikt) -> 'RadioStationList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The RadioStationList of this RadioStationList.  # noqa: E501
        :rtype: RadioStationList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def items(self) -> List[RadioStation]:
        """Gets the items of this RadioStationList.


        :return: The items of this RadioStationList.
        :rtype: List[RadioStation]
        """
        return self._items

    @items.setter
    def items(self, items: List[RadioStation]):
        """Sets the items of this RadioStationList.


        :param items: The items of this RadioStationList.
        :type items: List[RadioStation]
        """
        if items is None:
            raise ValueError("Invalid value for `items`, must not be `None`")  # noqa: E501

        self._items = items
