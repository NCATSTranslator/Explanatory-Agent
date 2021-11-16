import json
import datetime


class clsLogEvent:
    def __init__(self, identifier: str, level: str, code: str, message: str):
        self.timestamp: datetime = datetime.datetime.utcnow().isoformat()[:19]
        self.identifier: str = identifier
        self.level: str = level
        self.code: str = code
        self.message: str = message

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
