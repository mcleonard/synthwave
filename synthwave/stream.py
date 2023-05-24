import random
from typing import List

from synthwave import Event


class Stream:
    def __init__(self, events: List[Event]):
        self.events = events

    def generate_one(self):
        event = random.choice(self.events)
        return event.sample()

    def generate(self):
        while True:
            yield self.generate_one()
