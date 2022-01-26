import elasticsearch

host = 'host.docker.internal'
credentials = ('elastic', 'changeme')

es = elasticsearch.Elasticsearch(
    hosts=[host],
    http_auth=credentials,
    scheme="http",
    port=9200,
)

index_name = 'sov_sci'
es.indices.delete(index=index_name)
es.indices.create(index=index_name)
es.indices.close(index=index_name)
settings = {
    "analysis": {
        "filter": {
            "shingle": {
                "max_shingle_size": "3",
                "min_shingle_size": "2",
                "type": "shingle"
            },
            "synonym": {
                "type": "synonym",
                "synonyms": [
                ]
            },
            "search_synonym": {
                "ignore_case": "true",
                "type": "synonym",
                "synonyms": [
                    "пончо,накидка"
                ]
            },
            "ru_stopwords": {
                "type": "stop",
                "stopwords": "а,без,более,бы,был,была,были,было,быть,в,вам,вас,весь,во,вот,все,всего,всех,вы,где,да,даже,для,до,его,ее,если,есть,еще,же,за,здесь,и,из,или,им,их,к,как,ко,когда,кто,ли,либо,мне,может,мы,на,надо,наш,не,него,нее,нет,ни,них,но,ну,о,об,однако,он,она,они,оно,от,очень,по,под,при,с,со,так,также,такой,там,те,тем,то,того,тоже,той,только,том,ты,у,уже,хотя,чего,чей,чем,что,чтобы,чье,чья,эта,эти,это,я,a,an,and,are,as,at,be,but,by,for,if,in,into,is,it,no,not,of,on,or,such,that,the,their,then,there,these,they,this,to,was,will,with"
            }
        },
        "analyzer": {
            "name_analyzer": {
                "filter": [
                    "lowercase",
                    "russian_morphology",
                    "english_morphology",
                    "ru_stopwords"
                ],
                "char_filter": [
                    "e_char_filter"
                ],
                "type": "custom",
                "tokenizer": "standard"
            },
            "synonym": {
                "filter": [
                    "synonym"
                ],
                "tokenizer": "whitespace"
            },
            "search_analyzer": {
                "filter": [
                    "lowercase",
                    "russian_morphology",
                    "english_morphology",
                    "ru_stopwords",
                    "synonym"
                ],
                "char_filter": [
                    "e_char_filter"
                ],
                "type": "custom",
                "tokenizer": "standard"
            },
            "phrase": {
                "filter": [
                    "lowercase",
                    "shingle"
                ],
                "type": "custom",
                "tokenizer": "standard"
            },
            "longtext_analyzer": {
                "filter": [
                    "lowercase",
                    "russian_morphology",
                    "english_morphology"
                ],
                "char_filter": [
                    "e_char_filter"
                ],
                "type": "custom",
                "tokenizer": "standard"
            }
        },
        "char_filter": {
            "e_char_filter": {
                "type": "mapping",
                "mappings": [
                    "Ё => Е",
                    "ё => е"
                ]
            }
        }
    },
}

es.indices.put_settings(body=settings, index=index_name)

mapping = {
    "properties": {
        "person_link": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "photo_url": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "page_title": {
            "type": "text",
            "analyzer": "name_analyzer"
        },
        "page_title_suggest": {
            "type": "text",
            "analyzer": "phrase"
        },
        "description": {
            "type": "text",
            "analyzer": "longtext_analyzer"
        },
        "categories": {
            "type": "keyword",
        },
        "universities": {
            "type": "keyword",
        },
        "topic": {
            "type": "keyword",
        },
    }
}

es.indices.put_mapping(body=mapping, index=index_name)

es.indices.open(index=index_name)
