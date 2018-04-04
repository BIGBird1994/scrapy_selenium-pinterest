# coding=utf-8
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from scrapy import Request,Spider
from pymongo import MongoClient
from ..items import PinterestItem
from selenium import webdriver
from re import findall,search
from time import sleep
from lxml import html
import logging
import time


class spider(Spider):
    name = 'pinterest'
    start_urls = [
                    # 'https://www.pinterest.com/pin/719872321658227189/'
                    'https://www.pinterest.com/search/pins/?q=stussy&rs=typed&term_meta[]=stussy%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=streetwear&rs=typed&term_meta[]=streetwear%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=topman&rs=typed&term_meta[]=topman%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=topshop%20women&rs=typed&term_meta[]=topshop%7Ctyped&term_meta[]=women%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=zara&rs=typed&term_meta[]=zara%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=mens%20sweater',
                    'https://www.pinterest.com/search/pins/?q=womens%20sweater',
                    'https://www.pinterest.com/search/pins/?rs=ac&len=2&q=korea%20street%20style%20men&eq=korea%20street%20style&etslf=2440&term_meta[]=korea%7Cautocomplete%7Cundefined&term_meta[]=street%7Cautocomplete%7Cundefined&term_meta[]=style%7Cautocomplete%7Cundefined&term_meta[]=men%7Cautocomplete%7Cundefined',
                    'https://www.pinterest.com/search/pins/?q=korea%20street%20style%20women&rs=guide&term_meta[]=korea%7Cautocomplete%7Cundefined&term_meta[]=street%7Cautocomplete%7Cundefined&term_meta[]=style%7Cautocomplete%7Cundefined&add_refine=women%7Cguide%7Cword%7C1',
                    'https://www.pinterest.com/search/pins/?q=korea%20fashion&rs=typed&term_meta[]=korea%7Ctyped&term_meta[]=fashion%7Ctyped',
                    'https://www.pinterest.com/search/pins/?q=womens%20fashion%20spring&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=womens%20clothing&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=womens%20casual%20outfits&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=womens%20summer%20fashion&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=womens%20fashion%20winter&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=womens%20fashion%fall&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=spring%20outfits%20women&source_id=ygXUz7jp&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=mens%20fashion%20casual&source_id=te7dwHpF&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=suits&source_id=te7dwHpF&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=mens%20fashion%20winter&source_id=te7dwHpF&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=mens%20outfits&source_id=te7dwHpF&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=mens%20fashion%20style&source_id=te7dwHpF&rs=related_search_story',
                    'https://www.pinterest.com/search/pins/?q=fashion&rs=rs&eq=&etslf=1886&term_meta[]=fashion%7Crecentsearch%7Cundefined',

                   ]
    allowed_domain = ['pinterest.com']
    logger = logging.getLogger(__name__)
    js = "var q=document.documentElement.scrollTop={}"
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["chrome.page.settings.loadImages"] = False
    url = 'https://www.pinterest.com/search/pins/?q={brand_name}%20{gender}%20{cloth_category}&rs=typed'

    def __init__(self):
        conn = MongoClient(host='localhost',port=27017)
        self.col = conn['siku']['brand']
        self.col_2 = conn['amazon']['cloth_category']
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(desired_capabilities=self.dcap,chrome_options=chrome_options, executable_path='/usr/local/bin/chromedriver')
        self._driver = webdriver.Chrome(desired_capabilities=self.dcap,chrome_options=chrome_options, executable_path='/usr/local/bin/chromedriver')

    def start_requests(self):
        brand_name = []
        cloth_category = []
        genders = ['men','women']
        cursor = self.col.find({})
        _cursor = self.col_2.find({})
        for data in cursor:
            brand_name.append(data['brand_name'])
        for _data in _cursor:
            cloth_category.append(_data['cloth_category'])
        for name in brand_name:
            for cate in cloth_category:
                for gender in genders:
                    url = self.url.format(brand_name=name,gender=gender,cloth_category=cate)
                    self.start_urls.append(url)
        for url in self.start_urls:
            yield Request(url=url,callback=self.parse)

    def parse(self, response):
        try:
            self.driver.get(response.url)
            sleep(1)
            i = 1
            while True:
                self.driver.execute_script(self.js.format(5000*i))
                self.logger.info('scroll 第%s次' % i)
                sleep(1)
                i += 1
                if i >= 65:
                    resp = html.fromstring(self.driver.page_source)
                    item = PinterestItem()
                    count = 0
                    for data in resp.xpath('//div[@class="GrowthUnauthPin_brioPin"]'):
                        source = data.xpath('div[2]/div[2]/a/@href')
                        if source:
                            item['source'] = source[0]
                        else:
                            item['source'] = ''
                        item['url'] = data.xpath('div[1]/a/@href')[0]
                        item['picture'] = data.xpath('div[1]/a/img/@src')[0]
                        item['title'] = data.xpath('div[1]/a/img/@alt')[0]
                        item['source_url'] = self.driver.current_url
                        item['time'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                        count += 1
                        self.logger.info('%s %s' % (count,item))
                        yield item
                    for href in resp.xpath('//div[@class="GrowthUnauthPinImage"]/a/@href'):
                        meta = {"source_url":self.driver.current_url}
                        yield Request(url='https://www.pinterest.com{}'.format(href),meta=meta, callback=self.parse_next)
                    self.driver.delete_all_cookies()
                    self.driver.refresh()
                    break
        except Exception as e:
            self.logger.info("%s" % e)

    def parse_next(self, response):
        try:
            self._driver.get(response.url)
            sleep(1)
            i = 1
            while True:
                self._driver.execute_script(self.js.format(5000*i))
                self.logger.info('scroll 第%s次' % i)
                sleep(1)
                i += 1
                if i >= 65:
                    resp = html.fromstring(self._driver.page_source)
                    item = PinterestItem()
                    count = 0
                    for data in resp.xpath('//div[@class="GrowthUnauthPin_brioPin"]'):
                        source = data.xpath('div[2]/div[2]/a/@href')
                        if source:
                            item['source'] = source[0]
                        else:
                            item['source'] = ''
                        item['url'] = data.xpath('div[1]/a/@href')[0]
                        item['picture'] = data.xpath('div[1]/a/img/@src')[0]
                        item['title'] = data.xpath('div[1]/a/img/@alt')[0]
                        item['current_url'] = self._driver.current_url
                        item['source_url'] = response.meta['source_url']
                        item['time'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                        count += 1
                        self.logger.info('%s %s' % (count,item))
                        yield item
                    self._driver.delete_all_cookies()
                    self._driver.refresh()
                    break
        except Exception as e:
            self.logger.info("%s" % e)




