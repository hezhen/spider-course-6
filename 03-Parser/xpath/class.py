# -*- coding: utf-8 -*-

from lxml import html
from lxml import etree

from bs4 import BeautifulSoup


filename = 'Steve Jobs - Wikipedia.html'

with open(filename, 'r') as f:
    content = f.read()

tree = etree.HTML(content)

print( '--------------------------------------------')
print( '# different quote //*[@class="p-price J-p-5089237"')
print( '--------------------------------------------')
print( tree.xpath(u"//*[@class='p-price J-p-5089237']"))
print( '')
