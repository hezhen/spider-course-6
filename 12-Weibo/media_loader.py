# -*- coding: utf-8 -*-

import json
from threading import Thread
import requests
import re
import time

class MediaLoader:
    def __init__(self, json_obj):
        self.data = json_obj
        self.media_files = {}
        self.media_files['pics'] = []

    def get_media_files(self):
        type = None
        if 'pics' in self.data:
            self.parse_pics()
            type = 'pics'
        return type, self.media_files
        
    def parse_pics(self):
        for pic in self.data['pics']:
            url = pic['large']['url']
            self.media_files['pics'].append(url)
            t = Thread(target=self.download_pics, args=(url,))
            t.start()

    def download_pics(self, url):
        r = requests.get(url)
        with open(url[url.rfind('/')+1:], 'wb') as f:
            f.write(r.content)

if __name__ == "__main__":
    with open('test_data/pics.json', 'rb') as f:
        c = f.read()
    obj = json.loads(c)
    print(MediaLoader(obj[0]['status']).get_media_files())