import base64
import json
from configparser import NoSectionError

import boto3
from typing import Dict, Optional

from aws_xray_sdk.core import xray_recorder
from boto3_type_annotations.secretsmanager import Client
from boto3_type_annotations.sts import Client as SClient
from botocore.exceptions import ClientError
from notifications_python_client.notifications import NotificationsAPIClient

from .sender import Sender


class GovNotify(Sender):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.template_id: str = None
        self.template_vars: Optional[Dict] = None
        self.client = NotificationsAPIClient(
            api_key=self.get_api_key() or self.get_config_value(env_var='GOV_NOTIFY_KEY', section='GovNotify',
                                                                key='api_key'))

    @xray_recorder.capture('get_secret_value')
    def get_api_key(self) -> Optional[str]:
        try:
            role = self.get_config_value('SECRET_ROLE', 'AWS', 'secret_role')
            region = self.get_config_value('AWS_REGION', 'AWS', 'region')
            secret_name = self.get_config_value('GOV_NOTIFY_SECRET', 'GovNotify', 'secret_name')

            sts: SClient = boto3.client('sts')
            cred = sts.assume_role(RoleArn=role,
                                   RoleSessionName='GovNotifyKey')
            sess = boto3.Session(aws_access_key_id=cred['AccessKeyId'],
                                 aws_secret_access_key=cred['SecretAccessKey'],
                                 aws_session_token=cred['SessionToken'],
                                 region_name=region)
            sm: Client = sess.client('secretsmanager')
            sv = sm.get_secret_value(SecretId=secret_name)
            return json.loads(sv.get('SecretString')).get('api_key')
        except (ClientError, NoSectionError) as e:
            self.logger.warning('Failed to retrieve secret key from SecretsManager', exc_info=e)
            return

    def set_message(self, event: Dict):
        super().set_message(event)
        self.template_id = event.get('template_id')
        self.template_vars = event.get('template_vars')
        if self.attachment:
            # Gov notify only supports attaching PDFs that are less than 2MB
            if self.attachment_name.endswith('.pdf') and len(base64.b64decode(self.attachment, validate=True)) < 2e+6:
                self.template_vars['link_to_document'] = {'file': self.attachment}
            else:
                self.template_vars['s3_link'] = self.upload_attachment()

    def send(self):
        super().send()
        resp = None
        if self.message_type == 'email':
            resp = self.client.send_email_notification(template_id=self.template_id,
                                                       personalisation=self.template_vars,
                                                       email_address=self.to,
                                                       email_reply_to_id=self.get_config_value('GOV_NOTIFY_REPLY_TO',
                                                                                               section='GovNotify',
                                                                                               key='reply_to_id'))
        elif self.message_type == 'sms':
            resp = self.client.send_sms_notification(template_id=self.template_id, personalisation=self.template_vars,
                                                     phone_number=self.to)
        elif self.message_type == 'letter':
            raise NotImplementedError
        return resp
