import scrapy
from DWM.items import DwmItem
import json


class MySpider(scrapy.Spider):
    name = 'daiji'
    allowed_domains = ['https://www.daijiworld.com/home.aspx']
    start_urls = [
        'https://www.daijiworld.com/home.aspx',
    ]

    def parse(self, response):
        file = 'articles.jl'
        with open(file) as f:
            fileData = []
            for line in f:
                fileData.append(json.loads(line))
        for href in response.css('#form1 > div:nth-child(8) > div > div > div.col-md-8.borderRight > div:nth-child(1) '
                                 '> div.col-md-9.borderLeft > div:nth-child(2) > div > div > div:nth-child(2) > div >'
                                 ' ul > li > a::attr(href)'):
            ID = int(href.extract().split('=')[1])
            if not self.search_article(articles=fileData, refid=ID):
                request = scrapy.Request(url=href.extract(), callback=self.parseArticle, dont_filter=True)
                yield request
            else:
                yield None


    def parseArticle(self, response):
        item = DwmItem()
        identityNumber = int(response.url.split('=')[1])
        time = ''.join(response.css('#ContentPlaceHolder1_col7Content_lblDate::text').extract()).split(', ')[1]
        paragraph = ''

        for text in response.css('#ContentPlaceHolder1_col7Content_lblDesc > p::text'):
            paragraph += text.extract()
        title = ''.join(response.css('#ContentPlaceHolder1_col7Content_lblTitle::text').extract())
        image_urls = response.css('#ContentPlaceHolder1_col7Content_lblDesc > p > img::attr(src)').extract()
        item['ID'] = identityNumber
        item['time'] = time
        item['title'] = title
        item['text'] = paragraph
        item['image_urls'] = self.url_join(image_urls, response)
        return item

    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))
        return joined_urls

    def search_article(self, articles, refid):
        for article in articles:
            if int(article['ID']) == refid:
                return True
        return False

