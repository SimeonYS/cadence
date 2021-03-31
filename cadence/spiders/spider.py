import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CadenceItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CadenceSpider(scrapy.Spider):
	name = 'cadence'
	start_urls = ['https://cadencebank.com/about/news-and-press-releases?page=0']

	def parse(self, response):
		articles = response.xpath('//article[contains(@id,"detail-")][position()>1]')
		for article in articles:
			date = article.xpath('.//p/i/text()').get()
			post_links = article.xpath('.//div[@class="non-mobile-version"]//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@id="next-page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):

		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('(//section[@class="article-main full-width"])[position()>=1]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CadenceItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
