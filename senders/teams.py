import json
from typing import Dict

from requests import Request, Session, RequestException, TooManyRedirects, Response
from requests.adapters import HTTPAdapter

from .sender import Sender


class Teams(Sender):
    def __init__(self, config, web_hook_url=None):
        super().__init__(config)
        self.payload: Dict = None
        self.headers = {"Content-Type": "application/json"}
        self.http_timeout = 2
        self.web_hook_url = web_hook_url or self.get_config_value(env_var='TEAMS_URL', section='Teams',
                                                                  key='webhook_url')

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

    def send(self, req=None):
        super().send()
        req = req or Request(method='post', url=self.web_hook_url, json=json.dumps(self.payload),
                             headers=self.headers).prepare()
        try:
            resp = self.send_request(req, self.http_timeout)
            return resp.text
        except (RequestException, TooManyRedirects) as e:
            self.logger.exception(f"Request to Teams with url: {self.web_hook_url} Failed.", exc_info=e)
            raise

    @staticmethod
    def send_request(req: Request, timeout: int) -> Response:
        with Session() as s:
            s.mount("https://outlook.office.com/webhook/", HTTPAdapter(max_retries=10))
            resp = s.send(req, timeout=timeout)
            resp.raise_for_status()
            return resp

    def set_webhook_url(self, url):
        if url is not None:
            self.web_hook_url = url
