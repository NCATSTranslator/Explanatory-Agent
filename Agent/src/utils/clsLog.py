import json
import datetime
import copy


class clsLogEvent:
    def __init__(self, identifier: str, level: str, code: str, message: str):
        self.timestamp: datetime = datetime.datetime.utcnow().isoformat()
        self.identifier: str = copy.deepcopy(identifier)
        self.level: str = copy.deepcopy(level)
        self.code: str = copy.deepcopy(code)
        self.message: str = copy.deepcopy(message)

    def __repr__(self):
        return "{} {} {} {}: {}".format(self.identifier, self.timestamp, self.level, self.code, self.message)

    def dict(self):
        return {
            "identifier": self.identifier,
            "timestamp": self.timestamp,
            "level": self.level,
            "code": self.code,
            "message": self.message
        }

    def json(self):
        return json.dumps(self.dict())

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.identifier == other.identifier and self.level == other.level \
               and self.code == other.code and self.message == other.message
