from typing import Any

import re

camel_to_snake_pattern = re.compile(r"(?<!^)(?=[A-Z])")

def camel_case_to_snake_case(text):
    return camel_to_snake_pattern.sub("_", text).lower()

def make_schema(type) -> dict[str, Any]:
    # Adding metadata field to make it easy to write out as PySpark schema
    return {"nullable": False, "type": type, "metadata": {}}