import requests
import json


class ProxiesService:
    def __init__(self) -> None:
        self.source = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"

    def get(self):
        res = requests.get(self.source)

        print(json.load(res.content))
