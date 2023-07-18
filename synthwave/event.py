from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, List
from uuid import uuid4

from .field import Field
from .schema import Schema
from .utils import camel_case_to_snake_case

Sample = dict[str, Any]


class DataModel:
    """Class for designating data to be generated. Subclass this!"""

    @classmethod
    def sample(cls) -> Sample:
        """Sample one instance of event data"""
        fields = {
            camel_case_to_snake_case(field_name): field.sample()
            for field_name, field in vars(cls).items()
            if isinstance(field, Field)
        }
        return fields

    @classmethod
    def sample_many(cls, n: int) -> List[Sample]:
        """Sample many instances of the event data"""
        return [cls.sample() for _ in range(n)]

    @classmethod
    def sample_table(cls, n_rows: int) -> dict[str, list]:
        """Sample event data as a columnar data structure. The structure is a dictionary of lists,
        each list corresponds to a column, each column being an event field."""

        samples = cls.sample_many(n_rows)
        table = defaultdict(list)

        for sample in samples:
            for field, value in sample.items():
                table[field].append(value)

        return dict(table)

    @classmethod
    def schema(cls) -> Schema:
        fields = {
            camel_case_to_snake_case(field_name): field
            for field_name, field in vars(cls).items()
            if isinstance(field, Field)
        }
        return Schema(fields)


class Event(DataModel):
    """Subclass of DataModel that models an event similar to what you'd see from data SDKs like Segment.
    Automatically includes fields for the event name, event ID, and event timestamp."""

    @classmethod
    def sample(cls) -> Sample:
        """Sample one instance of event data"""
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
