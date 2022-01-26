from typing import List, Optional
from pydantic import BaseModel


class Parameter(BaseModel):
    """Mapping for faceted search parameter."""
    key: str
    values: List[str]


class ParamContainer(BaseModel):
    """Collection of parameters in request body."""
    params: List[Parameter]


def add_nested_filter(d):
    nested = {"nested": {
        "path": "params",
        "query": {
            "bool": {
                "must": [
                    # Keys go there
                ]

            }
        }
    }}
    d['query']['function_score']['query']['bool']['filter']['bool']['must'][0] \
        ['bool']['should'].append(nested)


def add_param_filter(d, key: str, values: List[str]):
    param_dict = {"bool": {
        "must": [
            {
                "term": {"params.name": key}
            },
            {
                "terms": {"params.value": values}
            },
        ]
    }}
    d['query']['function_score']['query']['bool']['filter']['bool']['must'][0] \
        ['bool']['should'][0]['nested']['query']['bool']['must'].append(param_dict)


def add_param_aggs(d):
    d['aggs']['params'] = {
        "nested": {
            "path": "params"
        },
        "aggs": {
            "name_agg": {
                "terms": {"field": "params.name", "size": 100},
                "aggs": {"val_aggs": {"terms": {"field": "params.value"}}}
            }
        }
    }


def build_search_request_dict(
        q: str,
        limit: Optional[int] = 3,
        offset: Optional[int] = 0,
        params: Optional[dict] = None,
        parameter_filters: Optional[ParamContainer] = None
) -> dict:
    """Elastic request parameters dictionary."""
    d = {
        "from": offset,
        "size": limit,
        # Aggregate results by product code to avoid duplicates

        "query": {
            "function_score": {
                # Actual query
                "query": {
                    "bool": {
                        "must": [
                            {
                                "bool": {
                                    "should": [
                                        # Text search
                                        {"simple_query_string": {
                                            "query": q,
                                            "analyzer": "search_analyzer",
                                            "fields": [
                                                "page_title^4",
                                                "description",
                                            ],
                                            "default_operator": "or",
                                            "minimum_should_match": "-35%"
                                        }, },
                                    ]
                                }
                            }

                        ],
                        "filter": {
                            "bool":
                                {"must":
                                    [  # Mandatory filtering conditions
                                        {"bool": {
                                            "should": [
                                                # Multi-select filtering
                                                # {"nested": {
                                                #     "path": "params",
                                                #     "query": {
                                                #         "bool": {
                                                #             "must": [
                                                #                 # Keys go there
                                                #             ]
                                                #
                                                #         }
                                                #     }
                                                # }}

                                            ]}
                                        },
                                        # Attribute existence filtering
                                        {"exists": {"field": "page_title"}},
                                    ]
                                }
                        }
                    },

                },
            },
        },

        # Facets
        "aggs": {
            "categories": {
                "terms": {
                    "field": "categories",
                    "size": 100
                }
            },

        }

    }

    # Parameters filtering specified in request body
    if parameter_filters and isinstance(parameter_filters, ParamContainer):
        print(parameter_filters.params)
        add_nested_filter(d)
        for param in parameter_filters.params[:1]:
            print(f'ADDING FILTER {param.key}')
            add_param_filter(d, param.key, param.values)

    return d


def check_items_exist(res) -> bool:
    """Checks whether any product returned."""
    return True if len(res['hits']['hits']) > 0 else False


def build_items(res) -> list:
    """Transformation of individual item to format expected on frontend."""
    items = []

    es_hits = res['hits']['hits']
    if es_hits:
        for elem in es_hits:
            hit = elem['_source']
            item_dict = {
                # '_id': hit['_id'],
                'categories': hit['categories'],
                'page_title': hit['page_title'],
                'person_link': hit['person_link'],
                'photo_link': hit['photo_url'],
                'topic': hit['topic'],
                'universities': hit['universities'],
            }
            items.append(item_dict)

    return items


def extract_suggest_items(res) -> list:
    """Formatting items from search to suggest format."""
    items = []

    es_hits = res['hits']['hits']
    if es_hits:
        for elem in es_hits:
            hit = elem['_source']

            item_dict = {
                'page_title': hit['page_title'],
                'person_link': hit['person_link'],
                'photo_link': hit['photo_url'],
            }
            items.append(item_dict)

    return items


def extract_total_result_count(res):
    return res['hits']['total']['value']


def transform_response(res):
    """Transforming Elasticsearch output to format expected on frontend."""
    result_dict = {
        "type": "plain",
        "status": "Ok",
        "time": res['took'],
        "results": {
            "total": extract_total_result_count(res),
            "items": build_items(res),
            # "aggregations": res['aggregations']['params']['name_agg']['buckets']
        }
    }

    return result_dict


def build_suggest_request_dict(term: str = None):
    """Body for ES suggest request."""
    d = {
        "suggest": {
            "text": term,
            "categories_suggest": {
                "term": {
                    "field": "categories",
                    "size": 10
                }
            },
            "simple_phrase": {
                "phrase": {
                    "field": "page_title_suggest",
                    "size": 5,
                    "gram_size": 3,
                    "max_errors": 2,
                    "direct_generator": [{
                        "field": "artcl_name_suggest",
                        "suggest_mode": "always"
                    }]
                }
            }
        }
    }

    return d


en_to_ru_layout = dict(zip(map(ord,
                               "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                               'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'),
                           "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                           'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё')
                       )
ru_to_en_layout = dict(zip(map(ord,
                               "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                               'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'),
                           "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                           'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'
                           )
                       )


def change_str_language(s: str) -> str:
    """Switches keyboard layout."""
    to_en = s.translate(ru_to_en_layout)
    to_ru = s.translate(en_to_ru_layout)
    if to_ru != s:
        return to_ru
    else:
        return to_en


def remove_punctuation(s: str) -> str:
    return s.replace(' ', '').replace('.', '').replace(',', '').replace('/', '').replace('-', '')


RU_TO_EN_SAME_UPPER_LETTERS_DICT = {
    'а': 'a',
    'в': 'b',
    'с': 'c',
    'е': 'e',
    'н': 'h',
    'к': 'k',
    'м': 'm',
    'о': 'o',
    'р': 'p',
    'т': 't',
    'х': 'x',
}


def check_same_ru_en_chars(s: str) -> bool:
    """Check string for same-looking in ru/en chars."""
    for key in RU_TO_EN_SAME_UPPER_LETTERS_DICT.keys():
        if key in s:
            return True
    return False


def replace_same_ru_to_en_chars(s: str) -> str:
    """Replace same-looking ru chars to en chars."""
    for key, value in RU_TO_EN_SAME_UPPER_LETTERS_DICT.items():
        s = s.replace(key, value)
    return s


suggester_list = [
    "categories_suggest",
    "simple_phrase"
]


def extract_keywords(res: dict, limit: int = 10) -> list:
    """Query keyword extraction from ES response."""
    keyword_list = []
    for suggester in suggester_list:
        options = res['suggest'][suggester][0]['options']
        if options:
            for option in options:
                keyword_list.append(option['text'])

    filtered_keywords = []
    for elem in keyword_list:
        if elem not in filtered_keywords:
            filtered_keywords.append(elem)

    return filtered_keywords[:limit]
