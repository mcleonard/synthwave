# File for defining events

from synthwave import Event, field


class AccountCreated(Event):
    user_id = field.UUID()

    properties = field.Object(
        first_name=field.GivenName(),
        last_name=field.FamilyName(),
        age=field.Integer(13, 95),
        email_address=field.EmailAddress(),
        location=field.Location() | field.Null(0.5),
    )


class PageView(Event):
    user_id = field.UUID(repeat_prob=0.1)
    page_url = field.URL()
    referring_url = field.URL("google.com")


# You can use a common Object field in multiple events
context = field.Object(
    app_version=field.OneOf(["1.0.0", "1.1.2", "1.2.0", "2.1.0"]),
    browser=field.OneOf(["Safari", "Chrome", "Firefox"]),
    browser_version=field.Integer(50, 100),
)


class AppOpen(Event):
    user_id = field.UUID(repeat_prob=0.1)
    context = context


class ImageExport(Event):
    user_id = field.UUID(repeat_prob=0.1)
    context = context
    properties = field.Object(format=field.OneOf(["jpeg", "png", "tiff", "gif"]))