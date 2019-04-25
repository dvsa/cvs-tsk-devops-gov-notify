import base64
from typing import Dict, Optional

from notifications_python_client.notifications import NotificationsAPIClient

from .sender import Sender


class GovNotify(Sender):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.template_id: str = None
        self.template_vars: Optional[Dict] = None
        self.client = NotificationsAPIClient(
            self.get_config_value(env_var='GOV_NOTIFY_KEY', section='GovNotify', key='api_key'))

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
