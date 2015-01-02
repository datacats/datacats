FROM ubuntu:14.04

MAINTAINER boxkite

RUN locale-gen en_US.UTF-8 && \
echo 'LANG="en_US.UTF-8"' > /etc/default/locale

USER root

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

#Configure webserver
ADD apache.wsgi /etc/ckan/apache.wsgi
ADD ckan_default.conf /etc/apache2/sites-available/ckan_default.conf
ADD ports.conf /etc/apache2/ports.conf
RUN a2ensite ckan_default
RUN a2dissite 000-default

RUN usermod -u 1000 www-data

CMD ["/usr/sbin/apachectl", "-DFOREGROUND"]
EXPOSE 5000
