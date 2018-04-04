# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field,Item




class PinterestItem(Item):
      url = Field()
      picture = Field()
      title = Field()
      source_url = Field()
      time = Field()
      current_url = Field()
      source = Field()