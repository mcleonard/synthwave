from datetime import datetime, timezone
from uuid import uuid4

from .field import Field
from .utils import camel_case_to_snake_case


class Event:
    """ Class for designating events to be generated. Subclass this! """
    @classmethod
    def sample(cls):
        fields = {
            camel_case_to_snake_case(field_name): field.sample()
            for field_name, field in vars(cls).items()
            if isinstance(field, Field)
        }

        event_data = {
            "event": camel_case_to_snake_case(cls.__name__),
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        event_data.update(fields)
        return event_data
