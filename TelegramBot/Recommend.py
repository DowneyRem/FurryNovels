import requests

import config


# 初始化推荐
def url_init_recommend(novel_id: int, limit: int = 3) -> str:
    return f"https://www.pixiv.net/ajax/novel/{novel_id}/recommend/init?limit={limit}&lang=zh"


# 后续推荐，传入参数应为推荐的小说id集合
def url_recommend(novel_list: list) -> str:
    url: str = "https://www.pixiv.net/ajax/novel/recommend/novels?"
    for novel in novel_list:
        url += f"novelIds%5B%5D{novel}&"
    return url.rstrip("&")


def do_recommend(url: str, method: str = "get") -> list:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47',
        'cookie': config.Pixiv_Cookie[0]
        }
    proxies = {
        "http": config.proxy_list[0],
        "https": config.proxy_list[0]
    }
    r = requests.request(method=method, url=url, headers=headers, proxies=proxies)
    novels = r.json()['body']['novels']
    return novels


def test():
    id = 18166741
    from PixivNovels import formatNovelInfo
    recommend_body = do_recommend(url_init_recommend(id))
    for item in recommend_body:
        print(formatNovelInfo(item['id']))


if __name__ == '__main__':
    tags: list = ['A', 'B', 'C']
    print(' '.join(list(map(lambda tag: '#' + tag, tags))))
    # print(config.Pixiv_Cookie[0])
    # test()