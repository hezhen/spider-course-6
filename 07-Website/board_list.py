import re
from lxml import etree
import requests

class BoardListCrawler:
    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Connection': "keep-alive",
        'Cookie': "Hm_lvt_9c7f4d9b7c00cb5aba2c637c64a41567=1540966746,1541124234,1541141377,1541150477; main[UTMPUSERID]=guest; main[XWJOKE]=hoho; Hm_lvt_bbac0322e6ee13093f98d5c4b5a10912=1545321687,1545382149,1545391501,1545395885; Hm_lpvt_bbac0322e6ee13093f98d5c4b5a10912=1545397118; main[UTMPKEY]=13080526; main[UTMPNUM]=6923; left-index=00000000000",
        'Host': "www.newsmth.net",
        'Referer': "http://www.newsmth.net/nForum/",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        'X-Requested-With': "XMLHttpRequest",
        'cache-control': "no-cache"
    }

    domain = 'http://www.newsmth.net/'

    base_url = domain + '/nForum/section/{}?ajax'

    def get_page(self, page_num):
        url = self.base_url.format(page_num)

        response = requests.get(url, headers = self.headers)

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
            board['topics'] = columns[5].text
            board['posts'] = columns[6].text
            boards.append(board)
            print(board)
        return boards

if __name__ == '__main__':
    boardListCrawler = BoardListCrawler()
    c = boardListCrawler.get_page(1)
    boardListCrawler.get_board_list(c)