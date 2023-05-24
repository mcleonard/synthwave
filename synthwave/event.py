from datetime import datetime, timezone
import re

from .field import Field

camel_to_snake_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case_to_snake_case(text):
    return camel_to_snake_pattern.sub("_", text).lower()


class Event:
    @classmethod
    def sample(cls):
        properties = {
            field_name: field.sample()
            for field_name, field in vars(cls).items()
            if isinstance(field, Field)
        }

        event_data = {
            "event": camel_case_to_snake_case(cls.__name__),
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "properties": properties,
        }
        return event_data
