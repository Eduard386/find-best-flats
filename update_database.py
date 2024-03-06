# USAGE - reads latest scrapy flats, finds unique flats, and saves them to database if they were absent there
import json

with open('database_realty.json', 'r', encoding='utf-8') as database_realty:
    database_realty_str = database_realty.read()
    database_realty_list = json.loads(database_realty_str)
    print('[INFO]: Database contained ' + str(len(database_realty_list)) + ' flats')

    with open('database_realty.json', 'w', encoding='utf-8') as database_realty_write:

        with open('tutorial/realty.json', 'r', encoding='utf-8') as scrapy_realty:
            scrapy_realty_str = scrapy_realty.read()
            scrapy_realty_list = json.loads(scrapy_realty_str)

            print('[INFO]: Scrapy brougth us ' + str(len(scrapy_realty_list)) + ' flats')
            # Leave only unique flats - remove duplicates by address, area and price criteria
            seen = set()
            unique_scrapy_realty_list = []
            for flat in scrapy_realty_list:
                t = tuple(flat.items())[0:3]
                if t not in seen:
                    seen.add(t)
                    unique_scrapy_realty_list.append(flat)
            print('[INFO]: And ' + str(len(unique_scrapy_realty_list)) + ' of them were unique')

            count = 0
            for flat in unique_scrapy_realty_list:
                if flat not in database_realty_list:
                    database_realty_list.append(flat)
                    count += 1
            print('[INFO]: Will add ' + str(count) + ' new flats to the database...')

            json.dump(database_realty_list, database_realty_write, ensure_ascii=False, indent=4)  # json
            print('[INFO]: Now database contains ' + str(len(database_realty_list)) + ' flats')
            database_realty_write.close()
