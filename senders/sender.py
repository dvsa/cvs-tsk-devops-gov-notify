import base64
import datetime
import logging
import mimetypes
import os
from abc import ABC, abstractmethod
from configparser import NoSectionError, ConfigParser
from typing import Dict, Optional, Any, Union
from urllib import parse

import boto3
from aws_xray_sdk.core import xray_recorder
from boto3_type_annotations.s3 import ServiceResource, Object
from botocore.exceptions import ClientError

boto3.set_stream_logger('', logging.INFO)


class Sender(ABC):
    def __init__(self, config) -> None:
        self.config = ConfigParser().read(config)
        self.logger = logging.getLogger(__name__)
        self.message_type: str = None
        self.to: str = None
        self.subject: str = None
        self.body: str = None
        self.attachment: Union[str, bytes] = None
        self.attachment_name: str = None
        self.s3_url: str = None

    def get_config_value(self, env_var: str, section: str, key: str) -> str:
        """
        Retrieves config value from environment variable 'env_var' and if it does not exist, tries to read it from
        the config.ini file.

        :param env_var: Name of the environment variable to lookup
        :param section: The .ini section i.e. [Sender]
        :param key: the .ini key i.e. value = example
        :returns: The value of the requested config value as a 'str'.
        :raises NoSectionError: This is raised when env_var does not exist and
        the requested config key also does not exist.
        """
        config_value: Optional[str] = os.getenv(env_var)
        if not config_value:
            try:
                config_value = self.config.get(section, key)
                self.logger.info(msg=f"Retrieved config value [{section}]\n{key}\n")
            except NoSectionError as e:
                self.logger.exception(f"Environment variable '{env_var}' not set and"
                                      f" [{section}]\n{key}\n in config.ini is not set", exec_info=e)
                raise
        return config_value

    @xray_recorder.capture('put')
    def upload_attachment(self) -> str:
        """
        Uploads an attachment to an S3 bucket for later use.
        :return: The URL of the uploaded attachment.
        """
        if self.attachment is None or self.attachment_name is None:
            raise ValueError('No attachment or attachment_name')
        elif self.attachment is not bytes:
            self.attachment: bytes = base64.b64decode(self.attachment, validate=True)
        bucket_name = self.get_config_value('BUCKET_NAME', 'S3', 'bucket_name')
        s3: ServiceResource = boto3.resource('s3')
        obj: Object = s3.Object(bucket_name, self.attachment_name)
        try:
            content_type, encoding = mimetypes.guess_type(self.attachment_name)
            obj.put(Body=self.attachment, Expires=datetime.datetime.now() + datetime.timedelta(weeks=1),
                    ContentType=content_type, ContentEncoding=encoding or '', ACL="bucket-owner-full-control")
        except ClientError as e:
            self.logger.exception("Error uploading attachment to S3", exc_info=e)
            raise
        key = parse.quote_plus(obj.key)
        bucket_region = 'eu-west-1'
        url = f"https://console.aws.amazon.com/s3/object/{bucket_name}/{key}?region={bucket_region}"
        self.logger.info(f"Uploaded object url: {url}")
        return url

    @abstractmethod
    def set_message(self, event: Dict) -> Any:
        """
        This should set 'to', 'subject', 'body' (as appropriate),
        and handle attachments (attaching to an email, saving to s3 and linking, etc.)
        from the event.

        :return: As desired.
        """
        self.logger.info(repr(event))
        self.message_type = event.get('message_type')
        self.to = event.get('to')
        self.subject = event.get('subject')
        self.body = event.get('body')
        self.attachment = event.get('attachment')
        self.attachment_name = event.get('attachment_name')

    @abstractmethod
    def send(self) -> Optional[str, Dict]:
        """
        This should 'send' the message and return a status message

        :return: As desired.
        """
        self.logger.info("Sending the message.")
