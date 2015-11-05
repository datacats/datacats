FROM datacats/web

MAINTAINER boxkite

ENV CKAN_HOME /usr/lib/ckan
ENV BRANCH release-v2.3-latest

RUN virtualenv $CKAN_HOME && \
    mkdir -p $CKAN_HOME /project /var/www/storage && \
    chown -R www-data:www-data /var/www && \
    git clone --depth 1 --branch $BRANCH https://github.com/ckan/ckan /project/ckan && \
    git clone --branch stable --depth 1 https://github.com/ckan/datapusher /project/datapusher && \
    $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckan-service-provider#egg=ckanserviceprovider && \
    $CKAN_HOME/bin/pip install -r /project/ckan/requirements.txt && \
    $CKAN_HOME/bin/pip install -e /project/ckan && \
    $CKAN_HOME/bin/pip install ckanapi && \
    $CKAN_HOME/bin/pip install -r /project/datapusher/requirements.txt
