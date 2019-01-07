from lxml import etree
import re
import requests

class TopicsCrawler:

    domain = 'https://www.newsmth.net'

    def get_content(self, board_url, page):
        querystring = {"ajax":"","p":str(page)}
        url = self.domain + board_url
        r = requests.get(url, params=querystring)
        self.html = r.text
        self.tree = etree.HTML(r.text)

    def get_max_page(self):
        
        pages = self.tree.xpath('//ol[@class="page-main"][1]/li')

        if len(pages) == 1:
            return 1

        last_page_text = pages[len(pages)-1].xpath('a')[0].text

        if last_page_text == '>>':
            return int(pages[len(pages)-2].xpath('a')[0].text)
        
        return int(last_page_text)

    def extract_tag_a(self, columns, index):
        title = columns[index].xpath('a')[0].text
        url = columns[index].xpath('a')[0].attrib['href']

        return title, url

    def extract_text(self, columns, index):
        tt = columns[index].text
        return tt if tt is not None else 0

    def get_post_list(self):
        rows = self.tree.xpath("//table[@class='board-list tiz']/tbody/tr")

        posts = []

        for row in rows:
            post = {}
            columns = row.xpath('td')
            post['title'], post['url'] = self.extract_tag_a(columns, 1)
            post['publish_time'] = self.extract_text(columns, 2)
            
            post['author_id'], post['author_url'] = self.extract_tag_a(columns, 3)
            post['rating'] = self.extract_text(columns, 4)
            post['num_likes'] = self.extract_text(columns, 5)
            post['num_replies'] = self.extract_text(columns, 6)
            
            posts.append(post)
        
        return posts

if __name__ == "__main__":
    plc = TopicsCrawler()
    content = plc.get_content('/nForum/board/AutoWorld', 1)
    print(plc.get_max_page())
    for post in plc.get_post_list():
        print(post)