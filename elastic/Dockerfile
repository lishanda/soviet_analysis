ARG ELK_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/elasticsearch/elasticsearch:7.11.1

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu

RUN bin/elasticsearch-plugin install https://github.com/sarafanfm/elasticsearch-analysis-morphology/raw/master/analysis-morphology-7.11.1.zip
