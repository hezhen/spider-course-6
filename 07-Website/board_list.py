import re
from lxml import etree
import requests
import time

class BoardListCrawler:
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

    domain = 'http://www.newsmth.net/'

    base_url = domain + '/nForum/section/{}?ajax'

    def __init__(self, interval = 1):
        self.interval = interval

    def get_pagination_content(self, page_num):
        url = self.base_url.format(page_num)
        response = requests.get(url, headers = self.headers)
        time.sleep(self.interval)
        return response.text

    def get_board_list(self, content):
        tree = etree.HTML(content)
        elements = tree.xpath('//table[@class="board-list corner"]/tbody/tr')
        boards = []
        for element in elements:
            board = {}
            columns = element.xpath('td')
            board['board_url'] = columns[0].xpath('a')[0].attrib['href']
            board['board_title'] = columns[0].xpath('a')[0].text

            if len(columns[1].xpath('a')) == 0:
                url = self.domain + board['board_url']
                response = requests.get(url, headers = self.headers)
                boards.append(self.get_board_list(response.text))
                continue

            board['manager_url'] = columns[1].xpath('a')[0].attrib['href']
            board['manager_id'] = columns[1].xpath('a')[0].text
            board['num_topics'] = columns[5].text
            board['num_posts'] = columns[6].text
            boards.append(board)
            print(board)
        return boards

if __name__ == '__main__':
    boardListCrawler = BoardListCrawler()
    for i in range(0,10):
        c = boardListCrawler.get_pagination_content(i)
        boardListCrawler.get_board_list(c)