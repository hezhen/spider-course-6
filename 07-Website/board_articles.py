import re
from lxml import etree
import requests
import time

class BoardArticleListCrawler:
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
        self.interval = interval
        pass

    def get_pagination_content(self, url, page_num):
        querystring = {"ajax":"","p":str(page_num)}
        response = requests.get(url, headers = self.headers, params=querystring)
        time.sleep(self.interval)
        return response.text

    def get_total_pages(self, content):
        tree = etree.HTML(content)
        page_list = tree.xpath('//ol[@class="page-main"]')[0].xpath('li')

        if len(page_list) == 1:
            return 1
        else:
            return int(page_list[len(page_list) - 2].xpath('a')[0].text)
        
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
    
    boardArticleListCrawler = BoardArticleListCrawler()
    content = boardArticleListCrawler.get_pagination_content(url, 1)
    print(boardArticleListCrawler.get_total_pages(content))
    boardArticleListCrawler.get_article_list(content)