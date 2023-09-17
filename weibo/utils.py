import os
import json
import time
import requests
from onepush import notify
from datetime import timedelta, timezone, datetime
from .logger import logger

MESSAGE_TEMPLATE = '''{split}
  Date: {today}
  SuperTalk: {name}
  Level: {level}
  Status: {is_sign}
'''

def now() -> datetime:
    beijing = timezone(timedelta(hours=8))
    utcnow = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utcnow.astimezone(beijing)

def today() -> str:
    return datetime.strftime(now(), "%Y-%m-%d")

def parse_result(result:dict):
    return MESSAGE_TEMPLATE.format(**result,split = "*"*25, today=today())

def load_config():
    if not (config := os.environ.get("WEIBO_PARAMS")):
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Load dotenv from local file.")
        config = os.environ.get("WEIBO_PARAMS")
    config = json.loads(config)
    return config["params"], config["cookie"], config["notifier"], config["key"]


def cookie_to_dict(cookie):
    if cookie and "=" in cookie:
        cookie = dict([line.strip().split("=", 1) for line in cookie.split(";")])
    return cookie


def nested_lookup(obj, key, with_keys=False, fetch_first=False):
    result = list(_nested_lookup(obj, key, with_keys=with_keys))
    if with_keys:
        values = [v for k, v in _nested_lookup(obj, key, with_keys=with_keys)]
        result = {key: values}
    if fetch_first:
        result = result[0] if result else result
    return result


def _nested_lookup(obj, key, with_keys=False):
    if isinstance(obj, list):
        for i in obj:
            yield from _nested_lookup(i, key, with_keys=with_keys)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if key == k:
                if with_keys:
                    yield k, v
                else:
                    yield v
            if isinstance(v, list) or isinstance(v, dict):
                yield from _nested_lookup(v, key, with_keys=with_keys)


def request(*args, **kwargs):
    is_retry = True
    count = 0
    max_retries = 3
    sleep_seconds = 5
    while is_retry and count <= max_retries:
        try:
            s = requests.Session()
            response = s.request(*args, **kwargs)
            is_retry = False
        except Exception as e:
            if count == max_retries:
                raise e
            logger.info("Request failed: {}".format(e))
            count += 1
            logger.info("Trying to reconnect in {} seconds ({}/{})...".format(sleep_seconds, count, max_retries))
            time.sleep(sleep_seconds)
        else:
            return response

def notify_user(title, content, notifier: str = None, key:str = None):
    if not notifier or not key:
        logger.info('No notification method configured ...')
        return
    logger.info('Preparing to send notification ...')
    result = json.loads(notify(notifier, key=key, title=title, content=content, group='Weibo').text)
    if (result.get('code') == 200):
        logger.info('Message delivered to user ...')