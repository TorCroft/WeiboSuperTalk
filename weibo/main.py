import re
from typing import List, Dict, Any
from .utils import (
    request,
    nested_lookup,
    load_config,
    parse_result,
    notify_user,
    logger,
    WeiboSignExpection
)


class Weibo:
    def __init__(self, verify_https: bool = False):
        """
        :param verify_https: 是否校验证书，False 对 127.0.0.1 内网服务可屏蔽警告
        """
        self.params, self.cookie, self.notifier, self.notifier_key = load_config()
        self.container_id = "100808fc439dedbb06ca5fd858848e521b8716"
        self.ua = "WeiboOverseas/6.2.9 (iPhone; iOS 16.6.1; Scale/3.00)"
        self.headers = {"User-Agent": self.ua}
        self.follow_data_url = "https://api.weibo.cn/2/cardlist"
        self.sign_url = "https://api.weibo.cn/2/page/button"
        self.event_url = f"https://m.weibo.cn/api/container/getIndex?containerid={self.container_id}_-_activity_list"
        self._follow_data: List[Dict[str, Any]] = []
        self.verify_https = verify_https

    @property
    def follow_data(self) -> List[Dict[str, Any]]:
        """获取关注列表并缓存"""
        if self._follow_data:
            return self._follow_data

        self.params["containerid"] = "100803_-_followsuper"
        try:
            response: Dict[str, Any] = request(
                "get",
                self.follow_data_url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookie,
                verify=self.verify_https,
            ).json()
        except Exception as e:
            logger.error(f"Failed to fetch follow data: {e}")
            raise WeiboSignExpection(message=str(e))

        if "errno" in response:
            msg = f'{response.get("errtype")}: {response.get("errmsg")}'
            logger.error(msg)
            raise WeiboSignExpection(message=msg)

        card_group = nested_lookup(response, "card_group", fetch_first=True) or []
        follow_list = [i for i in card_group if i.get("card_type") == "8"]

        for i in follow_list:
            action = nested_lookup(i, "action", fetch_first=True)
            request_url = "".join(re.findall("request_url=(.*)%26container", action)) if action else None
            follow = {
                "name": nested_lookup(i, "title_sub", fetch_first=True),
                "level": int(re.findall(r"\d+", i.get("desc1", "0"))[0]),
                "is_sign": nested_lookup(i, "name", fetch_first=True) != "签到",
                "request_url": request_url,
            }
            self._follow_data.append(follow)

        self._follow_data.sort(key=lambda k: k["level"], reverse=True)
        return self._follow_data

    def sign_one(self, follow: Dict[str, Any]) -> Dict[str, Any]:
        """为单个 SuperTalk 执行签到"""
        if follow["is_sign"] or not follow.get("request_url"):
            return follow

        params = self.params.copy()
        params.pop("containerid", None)
        params["request_url"] = follow["request_url"]

        try:
            response = request(
                "get",
                self.sign_url,
                params=params,
                headers=self.headers,
                cookies=self.cookie,
                verify=self.verify_https,
            ).json()
        except Exception as e:
            logger.error(f"Sign request failed for {follow['name']}: {e}")
            follow["sign_response"] = {"error": str(e)}
            return follow

        follow["sign_response"] = response
        if int(response.get("result", -1)) == 1:
            follow["is_sign"] = True
            follow["request_url"] = None
            logger.info(f"Successfully signed in {follow['name']}.")
        else:
            logger.warning(f"SuperTalk {follow['name']} sign-in failed.")

        return follow

    def sign(self) -> str:
        """执行所有 SuperTalk 签到"""
        raw_results: List[Dict[str, Any]] = [self.sign_one(follow) for follow in self.follow_data]

        # 生成结果字符串
        result_str = "\n".join(parse_result(f) for f in raw_results)
        result_str += "\n" + "*" * 25
        logger.info("\n" + result_str)

        # 未全部签到成功时通知
        if not all(f["is_sign"] for f in raw_results):
            notify_user(
                title="WeiboSuperTalk",
                content=result_str,
                notifier=self.notifier,
                key=self.notifier_key,
            )
        return result_str
