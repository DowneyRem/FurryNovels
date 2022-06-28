from pixivpy3 import AppPixivAPI
from platform import platform


class TokenRoundRobin:
    aapis = []
    tokenCount = 0
    callCount = 0

    def __init__(self, tokens: list):
        if "Windows" in platform():
            REQUESTS_KWARGS = {'proxies': {'https': 'http://127.0.0.1:10808', }}
        elif "Linux" in platform():
            REQUESTS_KWARGS = {}
        for t in tokens:
            if not isinstance(t, str):
                continue
            try:
                aapi = AppPixivAPI(**REQUESTS_KWARGS)
                aapi.set_accept_language("en-us")  # zh-cn
                aapi.auth(refresh_token=t)
                print("{} is OK!".format(t))
                self.aapis.append(aapi)
                self.tokenCount += 1
                # logging.info(f"{__file__}：网络可用")
            except Exception as e:
                print("请检查网络可用性或更换REFRESH_TOKEN")
                print("{} is not OK, ignoring!".format(t))
                # logging.error(e)
        print("Finished initialising, {} tokens is available.".format(self.tokenCount))

    def getAAPI(self) -> AppPixivAPI:
        self.callCount += 1
        print("Requesting token, returning # {}".format(self.callCount))
        return self.aapis[self.callCount % self.tokenCount]
