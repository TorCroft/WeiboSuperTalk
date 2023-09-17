from ..core import Provider


class ServerChan(Provider):
    name = 'serverchan'
    base_url = 'https://sc.ftqq.com/{}.send'
    site_url = 'https://sc.ftqq.com/3.version'

    _params = {'required': ['key', 'title'], 'optional': ['content']}

    def _prepare_url(self, key: str, **kwargs):
        self.url = self.base_url.format(key)
        return self.url

    def _prepare_data(self, title: str, content: str = None, **kwargs):
        self.data = {'text': title, 'desp': content}
        return self.data
