import logging
from typing import Optional

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from transformations import build_search_request_dict, check_items_exist, \
    extract_suggest_items, transform_response, build_suggest_request_dict, \
    change_str_language, extract_keywords, remove_punctuation

app = FastAPI(title='Backend Service')

debug = True

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if debug:
    host = 'host.docker.internal'
else:
    host = 'ip_address'

credentials = ('elastic', 'changeme')

es = Elasticsearch(
    hosts=[host],
    http_auth=credentials,
    scheme="http",
    port=9200,
)

# ES index
index_name = 'sov_sci'


@app.get("/")
async def read_root():
    """Stub endpoint."""
    res = es.search(index=index_name, body={"query": {"match_all": {}}})
    return res


@app.get("/health/")
async def health_check():
    """Service availability check endpoint."""
    result = 'dead'
    try:
        res = es.search(index=index_name, body={"query": {"match_all": {}}})
        if check_items_exist(res):
            result = "alive"
    except:
        logging.info('Problem connecting to ES')
    return result


@app.get("/search/")
async def search(
        q: str = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        nav_id: Optional[str] = None,
):
    """Placeholder GET request."""
    q = q.lower()

    d = build_search_request_dict(q, limit, offset, nav_id)
    res = es.search(index=index_name, body=d)

    if not check_items_exist(res):
        new_q = change_str_language(q)
        d = build_search_request_dict(new_q, limit, offset, nav_id)
        res = es.search(index=index_name, body=d)

    if not check_items_exist(res):
        new_q = remove_punctuation(new_q)
        d = build_search_request_dict(
            new_q,
            limit,
            offset,
            nav_id,
        )
        res = es.search(index=index_name, body=d)

    result = transform_response(res)
    return result


@app.get("/suggest/")
async def suggest(term: str = None, item_id: Optional[str] = 'true'):
    """Suggest endpoint."""

    d = build_suggest_request_dict(term)
    res = es.search(index=index_name, body=d)
    keywords = [term] + extract_keywords(res)

    if len(keywords) == 1:
        new_term = change_str_language(term)
        d = build_suggest_request_dict(new_term)
        res = es.search(index=index_name, body=d)
        keywords = [term] + extract_keywords(res)

    result = []
    for key in keywords:
        d = build_search_request_dict(key, limit=3)
        suggest_res = es.search(index=index_name, body=d)

        items = extract_suggest_items(suggest_res)
        if items:
            key_dict = {
                "request": key,
                "items": items
            }
            result.append(key_dict)

    return result
