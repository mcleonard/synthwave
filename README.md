# Synthwave: A Stream of Synthetic Events

The goal here is to provide a stream of synthetic data similar to events you would see in a normal business. This can be used to generate data for testing, development, and for learning.

The user defines the events they want emitted and this will write them to stdout, a file, or POST as JSON data to a URL (not tested yet).

Name data from [Kaggle](https://www.kaggle.com/datasets/nltkdata/names) and Decennial U.S. Census files.

## Installation

For now you'll want to use [Poetry](https://python-poetry.org) to install and run this. Clone this repo, change directories into it, then run `poetry install`.

## Usage

Define the events you want generated in a Python file. See `example.py` for an example:

```python
class AccountCreated(Event):
    user_id = field.UUID(repeat_prob=0.5)
    first_name = field.GivenName()
    last_name = field.FamilyName()
    age = field.Integer(13, 95)
    email_address = field.EmailAddress()
    location = field.Location()

class PageView(Event):
    user_id = field.UUID(repeat_prob=0.5)
    page_url = field.URL()
    referring_url = field.URL("google.com")
```

Then start the generation, in your terminal:

```
poetry run python -m synthwave -e example.py --interval 0.1
```

Here, `-e` points to the file with your event definitions and `--interval` sets the time between synthetic events. You can also write the events to a file with the `-o` flag (`synthwave -e example.py --interval 0.1 -o outfile.txt`)

The above definition will emit events that look like:
```
{
    'event': 'account_created', 
    'timestamp': '2023-05-24T04:34:12.873+00:00', 
    'properties': {
        'user_id': '8e2d6fba-4065-4fb0-ac6f-7c7a53b35189', 
        'first_name': 'Bill', 
        'last_name': 'Griffin', 
        'age': 63, 
        'email_address': 'temp@temp.com', 
        'location': 'Zigong, China'
    }
}

{
    'event': 'page_view', 
    'timestamp': '2023-05-24T04:34:11.871+00:00', 
    'properties': {
        'user_id': '7663a2a9-154b-4cc9-8a1b-44fcc806046f', 
        'page_url': 'https://wow.app/perpetual/arbitrary/egregious',
        'referring_url': 'https://google.com/sequentially/achingly/egregious'
    }
}
```