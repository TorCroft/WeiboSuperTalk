from ..core import Provider


class ServerChanTurbo(Provider):
    name = 'serverchanturbo'
    base_url = 'https://sctapi.ftqq.com/{}.send'
    site_url = 'https://sct.ftqq.com'

    _params = {
        'required': ['key', 'title'],
        'optional': ['content', 'channel', 'openid']
    }

    def _prepare_url(self, key: str, **kwargs):
        self.url = self.base_url.format(key)
        return self.url

    def _prepare_data(self,
                      title: str,
                      content: str = None,
                      channel: int = None,
                      openid: str = None,
                      **kwargs):
        self.data = {
            'text': title,
            'desp': content,
            'channel': channel,
            'openid': openid
        }
        return self.data
