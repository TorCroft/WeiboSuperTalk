# WeiboSuperTalk
Sign-in Program for Weibo.

## Usage
使用Stream抓包iOS 微博国际版，获得cookie和params，创建一个名为`WEIBO_PARAMS`的Secret，把下面json内容填写进去。
``` json
{
    "params": {
        "aid": "",
        "c": "",
        "containerid": "",
        "extparam": "",
        "from": "",
        "gsid": "",
        "i": "",
        "lang": "",
        "page": "",
        "s": "",
        "ua": "",
        "v_f": "",
        "v_p": ""
    },
    "cookie": {
        "SUB": "",
        "SUBP": ""
    },
    "notifier": "",
    "key": ""
}
```
