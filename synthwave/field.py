from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta, timezone
import decimal
import random
import string
from typing import Dict, List, Sequence, TypeVar
from uuid import uuid4

from synthwave import data
from .utils import camel_case_to_snake_case, make_schema

OneOfType = TypeVar("OneOfType", int, float, str)


class Field(ABC):
    """
    Abstract base class for fields. Must implement a ``sample`` method to
    be included in event data.
    """

    @abstractmethod
    def sample(self):
        pass

    @abstractmethod
    def schema(self) -> dict:
        """Returns a dictionary representing the field schema"""
        pass


class Object(Field):
    """
    A field representing an object consisting of other fields.

    .. code-block:: python

        from synthwave import Event, field

        class Example(Event):
            properties = field.Object(
                prop1=field.Integer(),
                prop2=field.Float()
            )

    """

    def __init__(self, **kwargs):
        for name, field in kwargs.items():
            self.__setattr__(name, field)

    def sample(self):
        fields = {
            camel_case_to_snake_case(field_name): field.sample()
            for field_name, field in vars(self).items()
            if isinstance(field, Field)
        }
        return fields

    def schema(self):
        fields: List[Dict] = []
        for field_name, field in vars(self).items():
            if isinstance(field, Object):
                schema = {"type": field.schema(), "nullable": False, "metadata": {}}
            else:
                schema = field.schema()
            schema["name"] = camel_case_to_snake_case(field_name)
            fields.append(schema)

        return {"fields": fields, "type": "struct"}


class Array(Field):
    """
    A field representing an an array of fields. Length of the generated array is
    random and controlled by the min_size and max_size parameters.

    .. code-block:: python

        from synthwave import Event, field

        class Example(Event):
            people = field.Array(
                field.Object(
                    name=field.FullName(),
                    age=field.Integer(0, 120)
                )
            )
            ids = field.Array(field.UUID())

    :param field: Field to generate in the array
    :param min_size: Minimum length of the generated array
    :param max_size: Maximium length of the generated array
    """

    def __init__(self, field: Field, min_size=1, max_size=2):
        self.field = field
        self.min_size = min_size
        self.max_size = max_size

    def sample(self):
        n_items = random.randrange(self.min_size, self.max_size + 1)
        return [self.field.sample() for _ in range(n_items)]

    def schema(self):
        """Return a dictionary representing this fields schema"""
        return {
            "type": {
                "containsNull": isinstance(self.field, Null),
                "elementType": self.field.schema(),
                "type": "array",
            },
            "nullable": False,
            "metadata": {},
        }


class Null(Field):
    """
    A field representing None / Null values.

    If used on its own, will always return None. Use with another field to sometimes
    return null values:

    ``field.Location() | field.Null(0.2)``

    will return None as the field value 20% of the time.
    """

    def __init__(self, probability: float):
        self.probability = probability
        self.not_null_field: Field | None = None

    def __ror__(self, other: Field) -> Field:
        self.not_null_field = other
        return self

    def sample(self):
        if self.probability == 0:
            return None
        elif random.random() < self.probability:
            return None
        elif self.not_null_field is not None:
            return self.not_null_field.sample()
        else:
            return None

    def schema(self):
        schema = dict(self.not_null_field.schema())
        schema["nullable"] = True
        return schema


class OneOf(Field):
    """
    Returns one of the options in the input sequence.
    """

    def __init__(self, options: Sequence[OneOfType]):
        self.options = options

    def sample(self) -> OneOfType:
        return random.choice(self.options)

    def schema(self) -> dict:
        option_type: str = ""
        option = self.options[0]
        if isinstance(option, int):
            option_type = "integer"
        elif isinstance(option, float):
            option_type = "float"
        elif isinstance(option, str):
            option_type = "string"
        else:
            option_type = "string"
        return make_schema(option_type)


class GivenName(Field):
    """
    Returns a random given ("first") name.
    """

    def sample(self):
        return random.choice(data.given_name)

    def schema(self) -> dict:
        return make_schema("string")


class FamilyName(Field):
    """
    Returns random family name ("last name", "surname").
    """

    def sample(self):
        return random.choice(data.family_name)

    def schema(self) -> dict:
        return make_schema("string")


class FullName(Field):
    """
    Returns a random full name.
    """

    def sample(self):
        return " ".join(
            [random.choice(data.given_name), random.choice(data.family_name)]
        )

    def schema(self) -> dict:
        return make_schema("string")


class Integer(Field):
    """
    Returns a random integer within a range ``low`` to ``high``.

    Defaults to return integers from 0 to 100
    """

    def __init__(self, low: int = 0, high: int = 100):
        self.low, self.high = low, high

    def sample(self):
        return random.randint(self.low, self.high)

    def schema(self) -> dict:
        return make_schema("integer")


class Long(Field):
    """
    Returns a random integer within a range ``low`` to ``high``, same as the
    Integer field, but designated as a 'long' type in the schema.

    Defaults to return integers from 0 to 100
    """

    def __init__(self, low: int = 0, high: int = 100):
        self.low, self.high = low, high

    def sample(self):
        return random.randint(self.low, self.high)

    def schema(self) -> dict:
        return make_schema("long")


class Float(Field):
    """
    Returns a random float within a range ``low`` to ``high``.

    Defaults to return floats from 0 to 100
    """

    def __init__(self, low: float = 0.0, high: float = 100.0):
        self.low, self.high = low, high

    def sample(self):
        return random.random() * (self.high - self.low) + self.low

    def schema(self) -> dict:
        return make_schema("float")


class Decimal(Field):
    """
    Returns a random Decimal within a range ``low`` to ``high``. Decimals are
    better able to represent values like prices compared to floats.

    Defaults to return Decimals from 0 to 100

    :param low: low bound for value, inclusive
    :param high: high bound for value, inclusive
    :param precision: string matching the precision you want for the decimal value
    :param cast_to: a type (like ``str``, ``float``, etc.) for type casting
    """

    def __init__(
        self, low=0.0, high=100.0, precision="1.00", cast_to: type | None = None
    ):
        self.low, self.high, self.precision = low, high, precision
        self.cast_to = cast_to

    def sample(self):
        value = decimal.Decimal(random.random() * (self.high - self.low) + self.low)
        out = value.quantize(decimal.Decimal(self.precision))
        if self.cast_to:
            return self.cast_to(out)
        return out

    def schema(self) -> dict:
        return make_schema(self.type.__name__ if self.type is not None else "float")


class Location(Field):
    """
    Returns a random city like ``"San Francisco, United States"``.
    """

    def sample(self):
        return random.choice(data.location)

    def schema(self) -> dict:
        return make_schema("string")


class Timestamp(Field):
    """
    Returns a POSIX timestamp in UTC, as a float by default

    :param start_time: (optional) datetime object designating the earliest time to be generated
    :param end_time: (optional) datetime object designating the latest time to be generated
    :param as_datetime: (optional) return the timestamp as a datetime object

    If both start_time and end_time are left as None, the timestamp returned is the current time when generated.
    """

    def __init__(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        as_datetime: bool = False,
        as_isoformat: bool = False
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.as_datetime = as_datetime
        self.as_isoformat = as_isoformat

    def sample(self):
        timestamp: datetime

        if self.start_time is None and self.end_time is None:
            timestamp = datetime.now(timezone.utc)

        if self.start_time is not None and self.end_time is None:
            time_range = datetime.now() - self.start_time
            rand_time = timedelta(
                seconds=random.randrange(0, int(time_range.total_seconds()))
            )
            timestamp = self.start_time + rand_time

        if self.end_time is not None and self.start_time is None:
            raise ValueError("end_time is only used if a start_time is also set")

        if self.start_time is not None and self.end_time is not None:
            time_range = self.end_time - self.start_time
            rand_time = timedelta(
                seconds=random.randrange(0, int(time_range.total_seconds()))
            )
            timestamp = self.start_time + rand_time
            
        if self.as_datetime:
            return timestamp
        elif self.as_isoformat:
            return timestamp.isoformat()
        else:
            return timestamp.timestamp()

    def schema(self) -> dict:
        if self.as_datetime:
            return make_schema("timestamp")
        elif self.as_isoformat:
            return make_schema("string")
        else:
            return make_schema("float")


class SKU(Field):
    """
    Returns a random string consisting of 8 alpha-numeric characters to be used as a SKU.
    """

    def sample(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def schema(self) -> dict:
        return make_schema("string")


class UUID(Field):
    """
    Returns a UUID as a string.

    Generated UUIDs are cached so they can be repeatedly returned. This is useful for
    simulating single users generating multiple events. The cache holds the 1000 most
    recently generated UUIDs.

    :param repeat_prob: Probability to repeat a UUID.
    """

    uuid_cache: deque[str] = deque([], maxlen=1000)

    def __init__(self, repeat_prob=0.0):
        self.repeat_prob = repeat_prob

    def sample(self):
        if self.repeat_prob and self.uuid_cache and random.random() < self.repeat_prob:
            uuid = random.choice(self.uuid_cache)
        else:
            uuid = str(uuid4())
            self.uuid_cache.append(uuid)
        return uuid

    def schema(self) -> dict:
        return make_schema("string")


class EmailAddress(Field):
    """
    Returns a randomly chosen email address.
    """

    def sample(self):
        return random.choice(data.email)

    def schema(self) -> dict:
        return make_schema("string")


class URL(Field):
    """
    Returns a random URL.

    :param domain: Use to specify the URL domain
    """

    def __init__(self, domain: str | None = None):
        self.domain = domain

    def sample(self):
        return "/".join(
            [
                "https:/",
                random.choice(("example.com", "cool.com", "wow.app", "yup.ai"))
                if self.domain is None
                else self.domain,
                random.choice(("perpetual", "generous", "sequentially", "ponderous")),
                random.choice(("vociferous", "arbitrary", "obsequious", "achingly")),
                random.choice(("obscure", "egregious", "syzygy", "zenith")),
            ]
        )

    def schema(self) -> dict:
        return make_schema("string")
