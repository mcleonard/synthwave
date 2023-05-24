from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timezone
import random
from typing import Sequence, TypeVar
from uuid import uuid4

from synthwave import data

T = TypeVar("T")


class Field(ABC):
    @abstractmethod
    def sample(self):
        pass


class OneOf(Field):
    def __init__(self, options: Sequence[T]):
        self.options = options

    def sample(self) -> T:
        return random.choice(self.option)


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


class Location(Field):
    def sample(self):
        return random.choice(data.locations)


class Timestamp(Field):
    def sample(self):
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class UUID(Field):
    uuid_cache: deque[str] = deque([], maxlen=100)

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
