FROM ubuntu:14.04

MAINTAINER boxkite

RUN locale-gen en_US.UTF-8 && \
echo 'LANG="en_US.UTF-8"' > /etc/default/locale

USER root

RUN apt-get -q -y update

# Install Node.js and lessc
RUN apt-get -q -y install nodejs npm
# -g is for global (on PATH)
RUN npm install -g less@1.7.5

# lessc command line tool depends on nodejs being installed as 'node' on the PATH.
RUN ln -s /usr/bin/nodejs /usr/bin/node

CMD ["/project/compile_less.sh"]
