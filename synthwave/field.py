from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timezone
import decimal
import random
import string
from typing import Sequence, TypeVar
from uuid import uuid4

from synthwave import data
from .utils import camel_case_to_snake_case

T = TypeVar("T")


class Field(ABC):
    """
    Abstract base class for fields. Must implement a ``sample`` method to
    be included in event data.
    """
    @abstractmethod
    def sample(self):
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


class OneOf(Field):
    """
    Returns one of the options in the input sequence.
    """

    def __init__(self, options: Sequence[T]):
        self.options = options

    def sample(self) -> T:
        return random.choice(self.options)


class GivenName(Field):
    """
    Returns a random given ("first") name.
    """

    def sample(self):
        return random.choice(data.given_name)


class FamilyName(Field):
    """
    Returns random family name ("last name", "surname").
    """

    def sample(self):
        return random.choice(data.family_name)


class FullName(Field):
    """
    Returns a random full name.
    """

    def sample(self):
        return " ".join(
            [random.choice(data.given_name), random.choice(data.family_name)]
        )


class Integer(Field):
    """
    Returns a random integer within a range ``low`` to ``high``.

    Defaults to return integers from 0 to 100
    """

    def __init__(self, low: int = 0, high: int = 100):
        self.low, self.high = low, high

    def sample(self):
        return random.randint(self.low, self.high)


class Float(Field):
    """
    Returns a random float within a range ``low`` to ``high``.

    Defaults to return floats from 0 to 100
    """

    def __init__(self, low: float = 0.0, high: float = 100.0):
        self.low, self.high = low, high

    def sample(self):
        return random.random() * (self.high - self.low) + self.low


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


class Location(Field):
    """
    Returns a random city like ``"San Francisco, United States"``.
    """

    def sample(self):
        return random.choice(data.location)


class Timestamp(Field):
    """
    Returns the timestamp when the event was generated in UTC, with millisecond precision
    """

    def sample(self):
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class SKU(Field):
    """
    Returns a random string consisting of 8 alpha-numeric characters to be used as a SKU.
    """

    def sample(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


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


class EmailAddress(Field):
    """
    Returns a randomly chosen email address.
    """

    def sample(self):
        return random.choice(data.email)


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
