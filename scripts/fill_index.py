import pprint

import elasticsearch
import pandas as pd
import json
import os

host = 'host.docker.internal'
credentials = ('elastic', 'changeme')

es = elasticsearch.Elasticsearch(
    hosts=[host],
    http_auth=credentials,
    scheme="http",
    port=9200,
)

index_name = 'sov_sci'


def add_doc(id, doc):
    es.create(index=index_name, id=id, document=doc)


global_category_name = 'soviet'
path = f'data/{global_category_name}/'

all_dicts = []
for filename in list(os.walk(path))[0][2]:
    with open(path + filename, encoding='utf-8') as f:
        data = json.load(f)['description']
        all_dicts.append(data)


filename = 'soviet_uni'
df = pd.read_json(f'universities/{filename}.json')
print(df.info())
length = len(df)
for index, item in df.iterrows():
    print(f'{index}/{length}')
    doc = {
        "person_link": item['person_link'],
        "photo_url": item["photo_url"],
        "page_title": item['page_title'],
        "page_title_suggest": item['page_title'],
        "categories": item['categories'],
        "universities": item['universities'],
        "topic": item['topic']
    }
    if all_dicts[index]:
        doc['description'] = all_dicts[index]
    add_doc(index, doc)