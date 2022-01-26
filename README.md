# soviet_analysis

Репозиторий веб-части проекта по анализу советских учёных.

## Инструменты

- Docker + Compose
- Elasticsearch 7.11.1
- Kibana
- Python 3.10
  - FastAPI
  - elasticsearch-py

## Запуск

Для запуска необходим Docker

`docker-compose up`

При помощи скриптов из папки `scripts` создаётся индекс и загружаются данные 
из JSON.

Инициализация индекса с mapping и analyzers:

`python create_index.py`

Заполнение индекса:

`python fill_index.py`