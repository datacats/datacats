FROM postgres:9.3

MAINTAINER boxkite

ADD ckan.sh /docker-entrypoint-initdb.d/ckan.sh

RUN apt-get update -yq

RUN apt-get install -y postgresql-9.3-postgis python-dev libxml2-dev libxslt1-dev libgeos-c1

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
