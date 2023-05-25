.. Synthwave documentation master file, created by
   sphinx-quickstart on Wed May 24 15:06:59 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Synthwave
=========

Synthwave is a Python package for generating a stream of synthetic JSON data. It was intially developed
to provide data for practicing with data engineering tools and workflows. However, it is very general
and can be used to generate JSON data for any use. For example, you can use this to test data pipelines,
generate data for unit or end-to-end tests, whatever else you can think of.

Synthetic data like names and email addresses were generated with GPT-3.

Installation
------------
Like normal: ``pip install synthwave``

Quickstart
----------
First you define your events in a file, say ``events.py``:

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

Then, start ``synthwave`` from the terminal:

.. code-block:: bash

   python -m synthwave -e events.py -o stdout

This will generate a stream of events like:

.. code-block:: python

   {
      'event': 'account_created',
      'event_id': '24a4f6ae-06dc-4df9-b67d-faac490ce890',
      'timestamp': '2023-05-25T15:22:55.419+00:00',
      'user_id': 'b18a2f0e-7257-41c0-8f1c-9c63c275b342',
      'properties': {
         'first_name': 'Parron',
         'last_name': 'Akori',
         'age': 95,
         'email_address': 'cleon@anache.net',
         'location': None
   }

These events are intended to simulate data you would see from SDKs from Amplitude, Segment, RudderStack, etc.
So, every event comes with an event name, a timestamp, and a unique event ID.

Every ``field`` object will create random data and add it to the output event. ``field.Null`` is used to
generate data that can be ``None | nil | null``. The parameter of ``field.Null`` sets how often the null
value occurs, 20% of the time in the above example.


Command Line Options
--------------------

Synthwave generation is started from the command line:

.. code-block:: bash

   python -m synthwave -e events.py -o stdout

You must point to a file where your events are defined ``-e filename.py``.

**Options:**

* ``-o``, ``--output``: Location for writing the event data. 

  * If not defined, will write data to ``stdout`` (the terminal). 
  * ``-o filename.txt`` writes the event data to the file ``filename.txt``.
  * ``-o https://url.com/webhook`` will POST the events to the URL as JSON data.

* ``-i``, ``--interval``: Time interval between events in seconds.
 
Fields Reference 
----------------

.. toctree::
   :maxdepth: 2

   field


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
