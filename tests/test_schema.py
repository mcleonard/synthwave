from synthwave import DataModel, field


def test_basic_schema():
    class TestModel(DataModel):
        first_name = field.GivenName()
        age = field.Integer(13, 95)
        height = field.Float(150, 200) | field.Null(0.2)

    schema = TestModel.schema()
    assert schema.to_dict() == {
        "fields": [
            {"nullable": False, "type": "string", "name": "first_name", "metadata": {}},
            {"nullable": False, "type": "integer", "name": "age", "metadata": {}},
            {"nullable": True, "type": "float", "name": "height", "metadata": {}},
        ]
    }


def test_array_schema():
    class TestModel(DataModel):
        ages = field.Array(field.Integer(13, 95) | field.Null(0.2))

    schema = TestModel.schema()
    assert schema.to_dict() == {
        "fields": [
            {
                "type": {
                    "containsNull": True,
                    "elementType": {
                        "nullable": True,
                        "type": "integer",
                        "metadata": {},
                    },
                    "type": "array",
                },
                "nullable": False,
                "name": "ages",
                "metadata": {},
            }
        ]
    }


def test_object_schema():
    class TestModel(DataModel):
        person = field.Object(name=field.FullName(), age=field.Integer(0, 100))

    print(TestModel.schema().to_dict())

    assert TestModel.schema().to_dict() == {
        "fields": [
            {
                "metadata": {},
                "name": "person",
                "nullable": False,
                "type": {
                    "fields": [
                        {
                            "nullable": False,
                            "type": "string",
                            "name": "name",
                            "metadata": {},
                        },
                        {
                            "nullable": False,
                            "type": "integer",
                            "name": "age",
                            "metadata": {},
                        },
                    ],
                    "type": "struct",
                },
            }
        ]
    }


def test_pyspark():
    class Candidates(DataModel):
        applications = field.Array(
            field.Object(
                id=field.Integer(55057855000, 55057856000),
                status=field.OneOf(["active", "rejected"]),
                last_activity_at=field.Timestamp(),
                custom_fields=field.Object(npi=field.SKU() | field.Null(0.98)),
            )
        )
        id = field.Integer(23909428000, 23909430000)

    schema = Candidates.schema().to_pyspark()
    print(schema)
    assert schema == {
        "fields": [
            {
                "metadata": {},
                "name": "applications",
                "nullable": False,
                "type": {
                    "containsNull": False,
                    "elementType": {
                        "fields": [
                            {
                                "metadata": {},
                                "name": "id",
                                "nullable": False,
                                "type": "integer",
                            },
                            {
                                "metadata": {},
                                "name": "status",
                                "nullable": False,
                                "type": "string",
                            },
                            {
                                "metadata": {},
                                "name": "last_activity_at",
                                "nullable": False,
                                "type": "timestamp",
                            },
                            {
                                "metadata": {},
                                "name": "custom_fields",
                                "nullable": False,
                                "type": {
                                    "fields": [
                                        {
                                            "metadata": {},
                                            "name": "npi",
                                            "nullable": True,
                                            "type": "string",
                                        }
                                    ],
                                    "type": "struct",
                                },
                            },
                        ],
                        "type": "struct",
                    },
                    "type": "array",
                },
            },
            {"metadata": {}, "name": "id", "nullable": False, "type": "integer"},
        ],
        "type": "struct",
    }
