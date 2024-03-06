import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'flatfy'

    def start_requests(self):
        urls = ['https://flatfy.ua/uk/search?geo_id=1&page=2&room_count=1&section_id=1&sub_geo_id=28756']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': 'socks5h://127.0.0.1:9051'})

    def parse(self, response):
        for flat in response.css('div.realty-content-layout'):
            yield {
                'title': flat.css('h3.realty-preview__title.realty-preview__title--with-geo a::text').get(),
                'price': flat.css('div.realty-preview__price::text').get().replace(" ", "").replace(" ", "")[:-1],
                'rooms': flat.css('span.realty-preview__info.realty-preview__info--rooms::text').get(),
                'url': 'https://flatfy.ua' + flat.css('h3.realty-preview__title.realty-preview__title--with-geo a::attr(href)').get()
            }

        next_page = response.css('a[data-event-label="next"]::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
