import dataclasses
import json


class DataClassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return o.__dict__
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
