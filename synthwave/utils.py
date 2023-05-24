import re

camel_to_snake_pattern = re.compile(r"(?<!^)(?=[A-Z])")

def camel_case_to_snake_case(text):
    return camel_to_snake_pattern.sub("_", text).lower()