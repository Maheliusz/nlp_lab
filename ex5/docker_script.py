# coding=utf8

import os

import requests

already_parsed = os.listdir('./after')

for bill_name in sorted(os.listdir('./ustawy')):
    if bill_name not in already_parsed:
        with open('./ustawy/' + bill_name, 'r', encoding='utf-8') as bill:
            with open('./after/' + bill_name, 'w', encoding='utf-8') as file:
                data = bill.read()
                response = requests.post('http://localhost:9200',
                                         data=data.lower().replace("[^\w\s]+", " ").encode('utf-8'))
                file.write(response.text)
                print("{} done".format(bill_name))
