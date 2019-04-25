from .sender import Sender


class Teams(Sender):
    def __init__(self, config):
        super().__init__(config)
        self.data = {}
        self.web_hook_url = self.get_config_value(env_var='TEAMS_URL', section='Teams', key='webhook_url')

    def set_message(self, event):
        raise NotImplementedError
        pass

    def send(self):
        raise NotImplementedError
        pass
