import scrapy

goloseevskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002248/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 5608
darnitskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002242/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 6069
desnyanskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002241/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 559
dneprovskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002243/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 2318
obolonskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002247/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 2020
pecherskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002249/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 8248
podolskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002250/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 1623
svyatoshenskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1003198/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 1615
solomenskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002246/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 3492
shevchenkovskiy = 'https://100realty.ua/realty_search/apartment/sale/r_1002253/nr_1/f_notfirst,notlast/cur_4/kch_2'  # 5149

class FlatsSpider(scrapy.Spider):
    name = 'realty'

    def start_requests(self):
        urls = [goloseevskiy, darnitskiy, desnyanskiy, dneprovskiy, obolonskiy,
                pecherskiy, podolskiy, svyatoshenskiy, solomenskiy, shevchenkovskiy]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': 'socks5h://127.0.0.1:9051'})

    def parse(self, response):
        for flat in response.css('.realty-object-card'):
            district = ''
            if '1002248' in response.request.url: district = 'Goloseevcki'
            elif '1002242' in response.request.url: district = 'Darnitskiy'
            elif '1002241' in response.request.url: district = 'Desnyanskiy'
            elif '1002243' in response.request.url: district = 'Dneprovskiy'
            elif '1002247' in response.request.url: district = 'Obolonskiy'
            elif '1002249' in response.request.url: district = 'Pecherskiy'
            elif '1002250' in response.request.url: district = 'Podolskiy'
            elif '1003198' in response.request.url: district = 'Svyatoshenskiy'
            elif '1002246' in response.request.url: district = 'Solomenskiy'
            elif '1002253' in response.request.url: district = 'Shevchenkovskiy'
            yield {
                'address': flat.css('.object-address a::text').get(),
                'area': int(flat.css('.object-square .value::text').re('[0-9]+')[0]),
                'price_on_web': int(flat.css('.usd-price-value::text').re(r'^([^$]+)')[0].replace(" ", "")),
                'url': 'https://100realty.ua' + flat.css('.object-address a::attr(href)').get(),
                'district': district
            }

        next_page = response.css('.pager-next a::attr(href)').getall()[0]   # there are 2 links
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
