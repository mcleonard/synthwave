# File for defining events

from synthwave import Event, field


class AccountCreated(Event):
    user_id = field.UUID(0.5)
    first_name = field.GivenName()
    last_name = field.FamilyName()
    age = field.Integer(13, 95)
    email_address = field.EmailAddress()
    location = field.Location()


class PageView(Event):
    user_id = field.UUID(repeat_prob=0.5)
    page_url = field.URL()
    referring_url = field.URL("google.com")
