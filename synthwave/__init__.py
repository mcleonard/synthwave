# ruff: noqa: E402

from dataclasses import dataclass
import json
import pkgutil
from typing import List


# This needs to come before other imports to avoid circular imports
@dataclass
class Data:
    given_name: List[str]
    family_name: List[str]
    location: List[str]
    email: List[str]

data_json = pkgutil.get_data(__name__, "data.json")
data: Data = Data(**json.loads(data_json))

from .event import Event, DataModel  # noqa: F401
from .stream import Stream  # noqa: F401
