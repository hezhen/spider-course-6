import re
from lxml import etree
import requests
import time
import html

class ArticleCrawler:
    interval = 1

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
        'cache-control': "no-cache",
        'Postman-Token': "81c91fb1-a034-4060-95fc-e04ee71ec462"
    }

    def __init__(self, base_url):
        self.base_url = base_url
        self.pattern = re.compile('<.*?>')
    
    def set_base_url(self, url):
        self.base_url = url

    def go_page(self, page_num):
        time.sleep(self.interval)
        url = self.base_url + "&p=" + str(page_num)
        response = requests.get(url, headers = self.headers)
        return response.text

    def get_posts(self, content):
        tree = etree.HTML(content)
        elements = tree.xpath('//table[@class="article"]')
        page_indexes = tree.xpath('//ol[@class="page-main"]')[0].xpath('li')
        articles = []
        if len(page_indexes) == 1:
            total_pages = 1
        else:
            total_pages = int(page_indexes[len(page_indexes) - 2].xpath('a')[0].text)
        for element in elements:
            article = etree.tostring(elements[0].xpath('//td[@class="a-content"]')[0].xpath('p')[0])
            article = html.unescape(article.decode('GBK')).replace('<br/>', '\n')
            article = self.pattern.sub('', article)
            articles.append(article)
            print(article)
        return articles, total_pages

if __name__ == '__main__':
    url = 'http://www.newsmth.net/nForum/article/ChildEducation/806532?ajax'
    articleCrawler = ArticleCrawler(url)
    c = articleCrawler.go_page(1)
    posts, total_pages = articleCrawler.get_posts(c)
    print(total_pages)
    if total_pages > 1:
        for i in range(2, total_pages + 1):
            c = articleCrawler.go_page(i)
            posts.append(articleCrawler.get_posts(c))