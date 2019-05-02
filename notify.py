import json
import logging
import os
from pathlib import Path
from typing import Dict, Callable

from aws_xray_sdk.core import patch_all

from senders import GovNotify, Teams

patch_all()
logger = logging.getLogger(__name__)
local_path = Path(__file__).parent
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.ini')
CONFIG = Path(local_path / CONFIG_FILE)
SENDERS: Dict[str, Callable] = {'email': GovNotify, 'sms': GovNotify, 'teams': Teams}


class Handler:
    def __init__(self, event):
        self.event = event
        self.message_type = event.get('message_type')
        self.message = None
        self.data = None
        self.response = None
        try:
            if self.message_type in SENDERS:
                self.sender = SENDERS[event.get('message_type')](CONFIG)
            else:
                raise ValueError
        except ValueError as e:
            logger.exception(f'{type(self.message_type)} was not in {repr(SENDERS.keys())}, failing.', exc_info=e)
            raise
        self.message = self.sender.set_message(self.event)
        if self.message:
            logger.info(f'Message set. {type(self.sender).__name__} returned: {self.message}')

    def __call__(self, *args, **kwargs):
        return self.handle()

    def handle(self):
        self.data = self.sender.send()
        self.response = {"response": self.data or f'Success but no response from sender: {type(self.sender).__name__}'}
        return self.response


def handler(event, context) -> Dict:
    """

    :param event: See README.md for examples
    :param context: AWS Lambda Context
    :return: A Dict with response data
    """
    logger.info(f"Function Event: {repr(event)}")
    logger.info(f"Function Context: {repr(context)}")
    h = Handler(event)
    return h.handle()


if __name__ == '__main__':
    import argparse

    logger.info('Running locally')
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', help='Path to event json file', type=Path)
    arguments = parser.parse_args()

    event_path: Path = Path(__file__).parent / arguments.event
    logging.info(f"Using event file at: {event_path.resolve()}")
    with event_path.open() as event_file:
        evt = json.load(event_file)
        logger.info(repr(handler(evt, {})))
