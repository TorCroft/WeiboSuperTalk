import re
from .utils import (
    request,
    nested_lookup,
    cookie_to_dict,
    load_config,
    parse_result,
    notify_user,
    logger,
    WeiboSignExpection
)


class Weibo(object):
    def __init__(self):
        self.params, self.cookie, self.notifier, self.notifier_key = load_config()
        self.container_id = "100808fc439dedbb06ca5fd858848e521b8716"
        self.ua = "WeiboOverseas/6.2.9 (iPhone; iOS 16.6.1; Scale/3.00)"
        self.headers = {"User-Agent": self.ua}
        self.follow_data_url = "https://api.weibo.cn/2/cardlist"
        self.sign_url = "https://api.weibo.cn/2/page/button"
        self.event_url = f"https://m.weibo.cn/api/container/getIndex?containerid={self.container_id}_-_activity_list"
        self._follow_data = []

    @property
    def follow_data(self):
        if not self._follow_data:
            url = self.follow_data_url
            self.params["containerid"] = "100803_-_followsuper"
            # turn off certificate verification
            response: dict = request(
                "get",
                url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookie,
                verify=False,
            ).json()
            if "errno" in response:
                msg = f'{response.get("errtype")}: {response.get("errmsg")}'
                logger.error(msg)
                raise WeiboSignExpection(message=msg)

            card_group = nested_lookup(response, "card_group", fetch_first=True)
            follow_list = [i for i in card_group if i["card_type"] == "8"]

            # fmt: off
            for i in follow_list:
                action = nested_lookup(i, "action", fetch_first=True)
                request_url = ("".join(re.findall("request_url=(.*)%26container", action)) if action else None)
                follow = {
                    "name": nested_lookup(i, "title_sub", fetch_first=True),
                    "level": int(re.findall("\d+", i["desc1"])[0]),
                    "is_sign": False if nested_lookup(i, "name", fetch_first=True) == "签到" else True,
                    "request_url": request_url,
                }
                self._follow_data.append(follow)
            # fmt: on
            self._follow_data.sort(key=lambda k: (k["level"]), reverse=True)
        return self._follow_data

    # fmt: off
    def sign(self) -> str:
        raw_results = []
        for follow in self.follow_data:
            if not follow["is_sign"]:
                url = self.sign_url
                self.params["request_url"] = follow["request_url"]
                if self.params.get("containerid"):
                    del self.params["containerid"]
                # turn off certificate verification
                response = request(
                    "get",
                    url,
                    params=self.params,
                    headers=self.headers,
                    cookies=self.cookie,
                    verify=False,
                ).json()
                follow["sign_response"] = response
                if int(response.get("result", -1)) == 1:
                    follow["is_sign"] = True
                    follow["request_url"] = None
                    logger.info(f"Successfully signed in {follow['name']}.")
                else:
                    logger.info(f"SuperTalk {follow['name']} sign-in failed.")
            raw_results.append(follow)

        result_str = ""
        for result in raw_results:
            result_str += parse_result(result)
        result_str += "*" * 25
        logger.info("\n" + result_str)

        if all([i["is_sign"] for i in raw_results]) is False:
            notify_user(title="WeiboSuperTalk", content=result_str, notifier=self.notifier, key=self.notifier_key,)
        return result_str
    # fmt: on
