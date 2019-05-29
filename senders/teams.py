from typing import Dict

import requests
from requests import RequestException, HTTPError

from .sender import Sender, xray_recorder, patch

patch(['requests'])


class Teams(Sender):
    def __init__(self, config, web_hook_url=None):
        super().__init__(config)
        self.payload: Dict = {}
        self.headers = {"Content-Type": "application/json"}
        self.http_timeout = 2
        self.web_hook_url = web_hook_url or self.get_config_value(env_var='TEAMS_URL', section='Teams',
                                                                  key='webhook_url')

    @xray_recorder.capture('Set Teams Message')
    def set_message(self, event):
        super().set_message(event)
        try:
            if self.body.get('@type') == 'MessageCard':
                self.logger.info("Custom Message found")
                self.payload = self.body
        except AttributeError:
            self.logger.info("self.body is a str, continuing...")
            pass
        finally:
            if not self.payload:
                self.payload = {
                    "@type": "MessageCard",
                    "@context": "https://schema.org/extensions",
                    "summary": self.subject,
                    "title": self.subject,
                    "text": self.body,
                }
                self.logger.info(f"Message set: {self.payload}")
            else:
                self.logger.info(f"Custom Message set: {self.payload}")

    @xray_recorder.capture('Send Teams Message')
    def send(self, req=None):
        super().send()
        try:
            resp = requests.post(url=self.web_hook_url, json=self.payload, headers=self.headers,
                                 http_timeout=self.http_timeout)
            resp.raise_for_status()
            return resp.text
        except (RequestException, HTTPError) as e:
            self.logger.debug(e.request.body)
            self.logger.debug(e.response.text)
            self.logger.exception(f"Request to Teams with url: {self.web_hook_url} Failed.", exc_info=e)
            raise

    def set_webhook_url(self, url):
        if url is not None:
            self.web_hook_url = url
