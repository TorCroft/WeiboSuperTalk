from weibo.main import Weibo

if __name__ == "__main__":
    sign_event = Weibo(verify_https = True)
    sign_event.sign()
