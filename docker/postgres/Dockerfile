FROM postgres:9.3

MAINTAINER boxkite

ADD ckan.sh /docker-entrypoint-initdb.d/ckan.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
