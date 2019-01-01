import re
from lxml import etree
import requests
import time
import html
import global_var

class PostsCrawler:

    def __init__(self, interval = 1):
        self.pattern = re.compile('<.*?>')
        self.interval = interval
    
    def get_pagination_content(self, url, page_num):
        time.sleep(self.interval)
        querystring = {"ajax":"","p":str(page_num)}
        response = requests.get(url, headers = global_var.headers, params=querystring)
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
    posts_crawler = PostsCrawler()
    c = posts_crawler.get_pagination_content(url, 1)
    total_pages = posts_crawler.get_total_pages(c)
    posts = posts_crawler.get_posts(c)
    print(total_pages)
    if total_pages > 1:
        for i in range(2, total_pages + 1):
            c = posts_crawler.get_pagination_content(i)
            posts += posts_crawler.get_posts(c)