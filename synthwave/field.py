from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timezone
import decimal
import random
from typing import Sequence, TypeVar
from uuid import uuid4

from synthwave import data
from .utils import camel_case_to_snake_case

T = TypeVar("T")


class Field(ABC):
    @abstractmethod
    def sample(self):
        pass


class Object(Field):
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
    def __init__(self, probability: float):
        self.probability = probability
        self.not_null_field: Field | None = None

    def __ror__(self, other: Field) -> Field:
        self.not_null_field = other
        return self

    def sample(self):
        if random.random() < self.probability:
            return None
        elif self.not_null_field is not None:
            return self.not_null_field.sample()
        else:
            return None


class OneOf(Field):
    def __init__(self, options: Sequence[T]):
        self.options = options

    def sample(self) -> T:
        return random.choice(self.options)


class GivenName(Field):
    def sample(self):
        return random.choice(data.given_name)


class FamilyName(Field):
    def sample(self):
        return random.choice(data.family_name)


class FullName(Field):
    def sample(self):
        return " ".join(
            [random.choice(data.given_name), random.choice(data.family_name)]
        )


class Integer(Field):
    def __init__(self, low: int = 0, high: int = 100):
        self.low, self.high = low, high

    def sample(self):
        return random.randint(self.low, self.high)


class Float(Field):
    def __init__(self, low: float = 0.0, high: float = 100.0):
        self.low, self.high = low, high

    def sample(self):
        return random.random() * (self.high - self.low) + self.low


class Decimal(Field):
    def __init__(self, low=0.0, high=100.0, precision=2):
        self.low, self.high, self.precision = low, high, precision

    def sample(self):
        decimal.getcontext().prec = self.precision
        value = random.random() * (self.high - self.low) + self.low
        return decimal.create_decimal_from_float(value)


class Location(Field):
    def sample(self):
        return random.choice(data.locations)


class Timestamp(Field):
    def sample(self):
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class UUID(Field):
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
    def sample(self):
        # TODO: Generate this
        return "temp@temp.com"


class URL(Field):
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
