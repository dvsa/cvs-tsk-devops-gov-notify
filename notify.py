import json
import os
from logging import Logger

from aws_xray_sdk.core import patch_all
from pathlib import Path
from typing import Dict, Union

from senders import GovNotify, Teams

patch_all()
logger = Logger(__name__)
local_path = Path(__file__).parent
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.ini')
CONFIG = Path(local_path / CONFIG_FILE)
SENDERS: Dict[str, Union[GovNotify, Teams]] = {'email': GovNotify(CONFIG), 'sms': GovNotify(CONFIG),
                                               'teams': Teams(CONFIG)}


def handler(event, context) -> Dict:
    """

    :param event: This should be:
    {
      'message_type': '<email, sms, teams>',
      'to': 'example@example.com, +4407123456789, @johndoe',
      'subject': 'Example Alert', [Optional]
      'body': 'This is an Example Alert',
      'attachment': '<base64 encoded file'>, [Optional] (Can not be greater than 2MB for email or it can be uploaded to s3 and linked).
      'attachment_name': 'File Name of the above attachment', [Optional]
    }
    :param context: AWS Lambda Context
    :return: Simple Response
    """
    logger.info(f"Function Event: {repr(event)}")
    logger.info(f"Function Context: {repr(context)}")
    try:
        sender: Union[GovNotify, Teams] = SENDERS[event.get('message_type')]
        if sender is None:
            raise ValueError
    except ValueError as e:
        logger.exception('message_type was not set, failing.', exc_info=e)
        raise
    msg = sender.set_message(event)
    if msg:
        logger.info(f'Message set. {type(sender).__name__} returned: {msg}')
    data = sender.send()
    return {"response": data or f'no response from sender: {type(sender).__name__}'}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--event', help='Path to event json file', type=Path)
    args = parser.parse_args()
    with open(args.event) as event_file:
        evt = json.load(event_file)
    handler(evt, {})
