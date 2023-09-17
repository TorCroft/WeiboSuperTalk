from ..core import Provider


class Pushdeer(Provider):
    name = 'pushdeer'
    base_url = 'https://api2.pushdeer.com/message/push'
    site_url = 'http://www.pushdeer.com/dev.html'

    _params = {
        'required': ['key','title'],
        'optional': ['content', 'type (markdown or image)']
    }

    def _prepare_url(self, **kwargs):
        self.url = self.base_url
        return self.url

    def _prepare_data(self,
                      content: str = None,
                      key: str = None,
                      title: str = None,
                      type: str = None,
                      **kwargs):
        self.data = {
            'pushkey': key,
            'text': title,
            'desp': content,
            'type': 'markdown' if not type or type == 'markdown' else 'image'
        }
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
