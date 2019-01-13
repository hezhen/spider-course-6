# -*- coding: utf-8 -*-

import json
from threading import Thread
import requests
import re
import time

class pic_downloader():
    def get_media_files(self, html_doc):
        pic_urls = re.findall(r'<img.*\ssrc=\"(\/\/att.newsmth.net.*?)\"\s', html_doc)

        for url in pic_urls:
            url = 'http:' + url
            t = Thread(target=self.download_pics, args=(url,))
            t.start()

    def download_pics(self, url):
        r = requests.get(url)
        filename = re.findall(r'//att.newsmth.net/nForum/att/(.*)', url)[0].replace('/', '_') + '.jpg'
        with open(filename, 'wb') as f:
            f.write(r.content)

if __name__ == "__main__":
    with open('smth.html', 'r') as f:
        c = f.read()
    pic_downloader().get_media_files(c)