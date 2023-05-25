# This module will start the stream

from argparse import ArgumentParser
import importlib.util
import inspect
import json
from pathlib import Path
from time import sleep

import requests
import validators

import synthwave

parser = ArgumentParser()
parser.add_argument(
    "-e", "--events", required=True, type=str, help="Path to event definitions"
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    default="stdout",
    help="Where to write the event data. Can be stdout, a file path, or a URL",
)
parser.add_argument(
    "--interval",
    type=float,
    default=0.0,
    help="Time between events in the output stream",
)

args = parser.parse_args()

spec = importlib.util.spec_from_file_location("events", args.events)
module = importlib.util.module_from_spec(spec)
events = module
spec.loader.exec_module(module)

user_events = {
    name: val
    for name, val in vars(events).items()
    if inspect.isclass(val) and issubclass(val, synthwave.Event) and name != "Event"
}

stream = synthwave.Stream(list(user_events.values()))

print("Starting Synthwave. Press Ctrl + C to stop running.\n")
for event in stream.generate():
    if args.output == "stdout":
        print(event)
    elif validators.url(args.output):
        requests.post(args.output, json=event)
    elif Path(args.output).exists:
        with open(args.output, "a") as f:
            f.write(json.dumps(event) + "\n")

    # Stop running when the user presses Ctrl + C
    try:
        sleep(args.interval)
    except KeyboardInterrupt:
        break
