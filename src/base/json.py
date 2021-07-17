import dataclasses
import datetime
from decimal import Decimal
import json


class DataClassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return o.__dict__

        if isinstance(o, datetime.datetime):
            if o.tzinfo:
                # eg: '2015-09-25T23:14:42.588601+00:00'
                return o.isoformat('T')
            else:
                # No timezone present - assume UTC.
                # eg: '2015-09-25T23:14:42.588601Z'
                return o.isoformat('T') + 'Z'

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, Decimal):
            return float(o)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
