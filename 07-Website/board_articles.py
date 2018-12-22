import re
from lxml import etree
import requests

class BoardCrawler:
    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Connection': "keep-alive",
        'Cookie': "Hm_lvt_9c7f4d9b7c00cb5aba2c637c64a41567=1540966746,1541124234,1541141377,1541150477; Hm_lvt_bbac0322e6ee13093f98d5c4b5a10912=1545141414,1545296728,1545307040,1545321687; Hm_lpvt_bbac0322e6ee13093f98d5c4b5a10912=1545322427; main[UTMPUSERID]=guest; main[UTMPKEY]=68083653; main[UTMPNUM]=28355",
        'Host': "www.newsmth.net",
        'Referer': "http://www.newsmth.net/nForum/",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'X-Requested-With': "XMLHttpRequest",
        'cache-control': "no-cache"
    }

    def __init__(self, base_url):
        self.base_url = base_url
        pass

    def get_page(self, page_num):
        querystring = {"ajax":"","p":str(page_num)}
        response = requests.get(url, headers = self.headers, params=querystring)
        return response.text
        
    def get_article_list(self, content):
        tree = etree.HTML(content)
        elements = tree.xpath('//table[@class="board-list tiz"]/tbody/tr')
        articles = []
        for element in elements:
            article = {}
            columns = element.xpath('td')
            article['article_url'] = columns[1].xpath('a')[0].attrib['href']
            article['article_title'] = columns[1].xpath('a')[0].text
            article['publish_time'] = columns[2].text
            article['author_url'] = columns[1].xpath('a')[0].attrib['href']
            article['author_id'] = columns[1].xpath('a')[0].text
            articles.append(article)
            print(article)
        return articles

if __name__ == '__main__':
    url = 'http://www.newsmth.net/nForum/board/Travel'
    boardCrawler = BoardCrawler(url)
    content = boardCrawler.get_page(1)
    boardCrawler.get_article_list(content)