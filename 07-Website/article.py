import re
from lxml import etree
import requests
import time
import html

class ArticleCrawler:

    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Connection': "keep-alive",
        'Host': "www.newsmth.net",
        'Referer': "http://www.newsmth.net/nForum/",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'X-Requested-With': "XMLHttpRequest",
        'cache-control': "no-cache"
    }

    def __init__(self, interval = 1):
        self.pattern = re.compile('<.*?>')
        self.interval = interval
    
    def get_pagination_content(self, url, page_num):
        time.sleep(self.interval)
        querystring = {"ajax":"","p":str(page_num)}
        response = requests.get(url, headers = self.headers, params=querystring)
        return response.text

    def get_total_pages(self, content):
        tree = etree.HTML(content)
        page_indexes = tree.xpath('//ol[@class="page-main"]')[0].xpath('li')
        
        if len(page_indexes) == 1:
            total_pages = 1
        else:
            total_pages = int(page_indexes[len(page_indexes) - 2].xpath('a')[0].text)
        return total_pages

    def get_posts(self, content):
        tree = etree.HTML(content)
        elements = tree.xpath('//table[@class="article"]')
        posts = []

        for element in elements:
            post = etree.tostring(elements[0].xpath('//td[@class="a-content"]')[0].xpath('p')[0])
            post = html.unescape(article.decode('GBK')).replace('<br/>', '\n')
            post = self.pattern.sub('', post)
            posts.append(post)
        return posts

if __name__ == '__main__':
    url = 'http://www.newsmth.net/nForum/article/ChildEducation/806532'
    articleCrawler = ArticleCrawler()
    c = articleCrawler.get_pagination_content(url, 1)
    total_pages = articleCrawler.get_total_pages(c)
    posts = articleCrawler.get_posts(c)
    print(total_pages)
    if total_pages > 1:
        for i in range(2, total_pages + 1):
            c = articleCrawler.get_pagination_content(i)
            posts.append(articleCrawler.get_posts(c))