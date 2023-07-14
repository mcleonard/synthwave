from synthwave import Event, field

class ExampleEvent(Event):
    user_id = field.UUID()

    properties = field.Object(
        first_name=field.GivenName(),
        age=field.Integer(13, 95),
        location=field.Location() | field.Null(0.5),
    )

def test_sample():
    sample = ExampleEvent.sample()

    assert "user_id" in sample
    assert "properties" in sample
    assert "first_name" in sample["properties"]

def test_sample_many():
    samples = ExampleEvent.sample_many(3)

    assert len(samples) == 3

    sample = samples[0]
    assert "user_id" in sample
    assert "properties" in sample
    assert "first_name" in sample["properties"]

def test_sample_table():
    table = ExampleEvent.sample_table(3)

    assert isinstance(table, dict)
    assert "user_id" in table
    assert "properties" in table

    assert len(table["user_id"]) == 3
    assert len(table["properties"]) == 3