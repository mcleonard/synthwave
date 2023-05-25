Fields
======

Fields are used to specify the data to generate, for example:

.. code-block:: python

   from synthwave import Event, field

   class AccountCreated(Event):
      user_id = field.UUID()

      properties = field.Object(
         first_name=field.GivenName(),
         last_name=field.FamilyName(),
         age=field.Integer(13, 95),
         email_address=field.EmailAddress(),
         location=field.Location() | field.Null(0.2),
      )


Available Fields
----------------
.. automodule:: synthwave.field
   :members: