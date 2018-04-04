# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient



class PinterestPipeline(object):

    def __init__(self):
        coon = MongoClient(host='localhost',port=27017)
        self.col = coon['pinterest']['_street_snap']

    def process_item(self, item, spider):
        try:
            self.col.insert(dict(item))
            return item
        except Exception as e:
            print(e)
