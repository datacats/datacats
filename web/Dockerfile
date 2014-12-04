FROM ubuntu:14.04

MAINTAINER boxkite

RUN locale-gen en_US.UTF-8 && \
echo 'LANG="en_US.UTF-8"' > /etc/default/locale

#Set users and environment variables
USER root
ENV CKAN_HOME /usr/lib/ckan
ENV CKAN_CONFIG /etc/ckan/default

#Install the packages we need
RUN apt-get -q -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -q -y install \
        python-minimal \
        python-dev \
        python-virtualenv \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
        wget \
        postfix \
        build-essential \
        git-core \
        apache2 \
        libapache2-mod-wsgi

# Install CKAN
RUN virtualenv $CKAN_HOME #change to use site packages
RUN mkdir -p $CKAN_HOME $CKAN_CONFIG /var/www/storage
RUN chown -R www-data:www-data /var/www/
RUN git clone --depth 1 https://github.com/ckan/ckan.git $CKAN_HOME/src/ckan
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckan/requirements.txt
RUN $CKAN_HOME/bin/pip install -e $CKAN_HOME/src/ckan/
RUN ln -s $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini

RUN $CKAN_HOME/bin/paster make-config ckan $CKAN_CONFIG/production.ini
RUN $CKAN_HOME/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/production.ini" -e \
    "sqlalchemy.url             =   postgresql://ckan:password@db:5432/ckan" \
    "ckan.datastore.read_url    =   postgresql://ckan_datastore_readonly:password@db:5432/ckan_datastore" \
    "ckan.datastore.write_url   =   postgresql://ckan:ckan_datastore_readwrite@db:5432/ckan_datastore" \
    "solr_url                   =   http://solr:8080/solr"

#Configure webserver
ADD apache.wsgi $CKAN_CONFIG/apache.wsgi
ADD ckan_default.conf /etc/apache2/sites-available/ckan_default.conf
RUN a2ensite ckan_default

CMD ["/usr/sbin/apachectl", "-DFOREGROUND"]
EXPOSE 80
