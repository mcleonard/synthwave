from typing import Dict, List

from synthwave.field import Field, Object

from .utils import camel_case_to_snake_case


class Schema:
    def __init__(self, fields: Dict[str, Field]):
        self.fields = fields

    def to_dict(self):
        root: Dict[List[Dict]] = {"fields": []}
        for field_name, field in self.fields.items():
            if isinstance(field, Object):
                schema = {"type": field.schema(), "nullable": False, "metadata": {}}
            else:
                schema = field.schema()
            schema["name"] = camel_case_to_snake_case(field_name)
            root["fields"].append(schema)
        return root

    def to_pyspark(self):
        """Return a dictionary representing the schema. This conforms to the PySpark schema JSON format."""
        root = {"fields": [], "type": "struct"}
        for field_name, field in self.fields.items():
            if isinstance(field, Object):
                field_schema = field.schema()
                if "metadata" not in field_schema:
                    field_schema["metadata"] = {} 
                schema = {"metadata": {}, "type": field_schema, "nullable": False}
            else:
                schema = field.schema()
                if "metadata" not in schema:
                    schema["metadata"] = {}
            schema["name"] = camel_case_to_snake_case(field_name)
            root["fields"].append(schema)
        return root
