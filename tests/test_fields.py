from datetime import datetime, timezone
from decimal import Decimal
import string
from urllib.parse import urlparse

from synthwave import data, Event, field


def test_object():
    class TestObject(Event):
        properties = field.Object(value=field.Integer(0, 3))

    sample = TestObject.sample()
    assert "properties" in sample
    assert "value" in sample["properties"]

    assert sample["properties"]["value"] in {0, 1, 2, 3}


def test_array():
    class TestArray(Event):
        values = field.Array(field.FullName(), 1, 3)
        objects = field.Array(field.Object(values=field.OneOf([1, 2, 3])), 2, 5)

    event = TestArray.sample()

    assert len(event["values"]) >= 1 and len(event["values"]) <= 3
    assert len(event["objects"]) >= 2 and len(event["objects"]) <= 5

    assert isinstance(event["values"][0], str)

    assert isinstance(event["objects"][0], dict)
    assert event["objects"][0]["values"] in {1, 2, 3}


def test_null():
    class TestNull(Event):
        value = field.Integer() | field.Null(0.5)

    samples = TestNull.sample_many(100)

    num_nones = sum(int(s["value"] == None) for s in samples)
    assert num_nones > 35 and num_nones < 65


def test_one_of():
    class TestOneOf(Event):
        value = field.OneOf([1, 2, 3])

    events = TestOneOf.sample_many(100)
    assert events[0]["value"] in {1, 2, 3}

    assert set(event["value"] for event in events) == {1, 2, 3}


def test_names():
    class TestNames(Event):
        given = field.GivenName()
        family = field.FamilyName()
        full = field.FullName()

    sample = TestNames.sample()

    given_names = set(data.given_name)
    family_names = set(data.family_name)

    assert sample["given"] in given_names
    assert sample["family"] in family_names
    assert sample["full"].split(" ")[0] in given_names
    assert sample["full"].split(" ")[1] in family_names


def test_numbers():
    class TestNumbers(Event):
        ints = field.Integer(0, 5)
        floats = field.Float(0.0, 5.0)
        decimals = field.Decimal(0.0, 5.0)

    samples = TestNumbers.sample_many(10)

    assert all(
        isinstance(sample["ints"], int) and sample["ints"] in set(range(0, 6))
        for sample in samples
    )

    # Make sure it's not returning only one value
    assert not all(sample["ints"] == samples[0]["ints"] for sample in samples)

    assert all(
        isinstance(sample["floats"], float)
        and sample["floats"] > 0.0
        and sample["floats"] < 5.0
        for sample in samples
    )
    assert not all(sample["floats"] == samples[0]["floats"] for sample in samples)

    assert all(
        isinstance(sample["decimals"], Decimal)
        and sample["decimals"] > 0.0
        and sample["decimals"] < 5.0
        for sample in samples
    )
    assert not all(sample["decimals"] == samples[0]["decimals"] for sample in samples)


def test_location():
    class TestLocation(Event):
        location = field.Location()

    sample = TestLocation.sample()

    assert sample["location"] in set(data.location)


def test_timestamp():
    class TestTimestamp(Event):
        timestamp = field.Timestamp()

    sample = TestTimestamp.sample()

    assert (datetime.now(timezone.utc).timestamp() - sample["timestamp"]) < 1


def test_datetime():
    class TestDateTime(Event):
        datetime_as_str = field.DateTime()
        datetime_as_dt = field.DateTime(as_datetime=True)

    sample = TestDateTime.sample()
    assert isinstance(sample["datetime_as_dt"], datetime)
    assert isinstance(sample["datetime_as_str"], str)
    assert (
        datetime.now(timezone.utc).timestamp()
        - datetime.fromisoformat(sample["datetime_as_str"]).timestamp()
    ) < 1


def test_sku():
    class TestSKU(Event):
        sku = field.SKU()

    sample = TestSKU.sample()

    assert len(sample["sku"]) == 8
    assert all(
        ch in set(string.ascii_uppercase + string.digits) for ch in sample["sku"]
    )


def test_UUID():
    class TestUUID(Event):
        uuid = field.UUID(repeat_prob=0.2)

    samples = TestUUID.sample_many(100)

    # Checking if we get repeats. Unique UUIDs should be less than total UUIDs
    assert len(set(s["uuid"] for s in samples)) < len(samples)
    assert isinstance(samples[0]["uuid"], str)


def test_email():
    class TestEmail(Event):
        email = field.EmailAddress()

    sample = TestEmail.sample()

    assert sample["email"] in set(data.email)


def test_url():
    class TestURL(Event):
        url = field.URL()

    sample = TestURL.sample()

    # test will fail if this raises an exception
    urlparse(sample["url"])
