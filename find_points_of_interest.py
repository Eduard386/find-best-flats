import json
import argparse
from collections import Counter

# Scraped some data -> updated database -> found points of interest

# for every scrapy flat calculate "meter_price_calculated" =>
# "average_meter_price_calculated" =>
# "correct_price_calculated"

ap = argparse.ArgumentParser()
ap.add_argument('-min', '--minimum-difference', required=True, help='How much real price larger that web price')
ap.add_argument('-max', '--maximum-web-cost', required=True, help='How much real price larger that web price')
args = vars(ap.parse_args())

with open('database_realty.json', 'r', encoding='utf-8') as database_realty:
    database_realty_list = json.loads(database_realty.read())
    print('[INFO] Database contains ' + str(len(database_realty_list)) + ' unique flats')
    database_realty.close()


def get_flats_with_such_address_from_db(address: str):
    with open('database_realty.json', 'r', encoding='utf-8') as database_realty:
        database_realty_list = json.loads(database_realty.read())
        list_of_flats_with_same_address = [flat_dict for flat_dict in database_realty_list
                            if flat_dict['address'] == address]  # Filter python objects
        return list_of_flats_with_same_address


with open('points_of_interest_realty.json', 'w', encoding='utf-8') as points_of_interest_json:

    with open('tutorial/realty.json', 'r', encoding='utf-8') as scrapy_realty:
        all_scrapy_flats_list = json.load(scrapy_realty)  # Transform json input to python objects

        # Leave only unique flats - remove duplicates by address, area and price criteria
        seen = set()
        unique_scrapy_flats_list = []
        for flat in all_scrapy_flats_list:
            t = tuple(flat.items())[0:3]
            if t not in seen:
                seen.add(t)
                unique_scrapy_flats_list.append(flat)
        print('[INFO] Scrapy brougth us ' + str(len(all_scrapy_flats_list)) +
              ' flats, and ' + str(len(unique_scrapy_flats_list)) + ' flats were unique')

        # Find addresses under construction
        address_counter = Counter(flat['address'] for flat in unique_scrapy_flats_list)
        under_construction_flats_count = 0
        list_of_addresses_under_construction = []
        for flat in unique_scrapy_flats_list:
            for address in address_counter:
                if flat['address'] == address and address_counter[address] > 10:
                    if address not in list_of_addresses_under_construction:
                        list_of_addresses_under_construction.append(address)
                    flat['status'] = 'Under construction'
                    under_construction_flats_count = under_construction_flats_count + 1
        print('Found ' + str(under_construction_flats_count) + ' under construction flats, in '
              + str(len(list_of_addresses_under_construction)) + ' addresses')

        list_of_unique_scrapy_addresses = []  # should be list of unique addresses from initial json
        # Create list of just addresses
        for flat in unique_scrapy_flats_list:
            if flat['address'] not in list_of_unique_scrapy_addresses:
                list_of_unique_scrapy_addresses.append(flat['address'])
        print('Amount of unique scrapy addresses ' + str(len(list_of_unique_scrapy_addresses)))

        # Calculate and add meter_price for all scrapy flats
        for flat in unique_scrapy_flats_list:
            meter_price = int(round(flat['price_on_web'] / flat['area']))
            flat['meter_price_calculated'] = meter_price

        # Get "average meter price" for every Scrapy address, for same addresses from database
        # Find all flats in database with same unique Scrapy address
        points = []
        for address in list_of_unique_scrapy_addresses:
            if address not in list_of_addresses_under_construction:
                flats_with_scrapy_address_from_DB = get_flats_with_such_address_from_db(address=address)  # get list of flats with same Scrapy address from DB
                if flats_with_scrapy_address_from_DB:  # if such flats with same address were found
                    sum_of_meter_prices_in_same_address = 0

                    for flat in flats_with_scrapy_address_from_DB:  # for every flat with such address
                        meter_price_from_db = int(round(flat['price_on_web'] / flat['area']))  # calculate meter price
                        flat['meter_price_calculated'] = meter_price_from_db
                        sum_of_meter_prices_in_same_address += flat['meter_price_calculated']  # calculate sum of meter prices

                    average_meter_price = int(round(sum_of_meter_prices_in_same_address /
                                                    len(flats_with_scrapy_address_from_DB)))  # Calculate average meter price

                for flat in unique_scrapy_flats_list:  # for every flat from Scrapy
                    if flat['address'] == address:
                        flat['average_meter_price_calculated'] = average_meter_price
                        flat['accuracy'] = len(flats_with_scrapy_address_from_DB)
                        flat['correct_price_calculated'] = flat['area'] * flat['average_meter_price_calculated']
                        flat['can_earn'] = (flat['correct_price_calculated'] - flat['price_on_web']) * 0.9
                        if flat['can_earn'] > int(args["minimum_difference"]) \
                                and 10000 < flat['price_on_web'] < int(args["maximum_web_cost"]):
                            points.append(flat)

        print('Found ' + str(len(points)) + ' interesting flats')
        sorted_points_by_accuracy_reversed = sorted(points, key=lambda k: k['accuracy'], reverse=True)

        # Save python dicts back into json
        json.dump(sorted_points_by_accuracy_reversed, points_of_interest_json, ensure_ascii=False, indent=4)  # json
        points_of_interest_json.close()
