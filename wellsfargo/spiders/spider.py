import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import WellsfargoItem
from itemloaders.processors import TakeFirst


class WellsfargoSpider(scrapy.Spider):
	name = 'wellsfargo'
	start_urls = ['https://newsroom.wf.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['GetPressReleaseListResult']:
			url = post['LinkToDetailPage']
			title = post['Headline']
			date = post['PressReleaseDate']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})


	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=WellsfargoItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
