FROM ubuntu:14.04

MAINTAINER boxkite

RUN locale-gen en_US.UTF-8 && \
echo 'LANG="en_US.UTF-8"' > /etc/default/locale

USER root

RUN apt-get -q -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -qy install python python-virtualenv git python-dev libxml2-dev libxslt-dev libz-dev

# We make a datacats user (will be used for shell and to install packages with pip)
RUN groupadd -r datacats && useradd -r -d /source -m -g datacats datacats

USER datacats

RUN virtualenv ~/venv


RUN echo $(which python)
# Currently we use Denis's fork.
RUN git clone http://github.com/deniszgonjanin/datapusher.git ~/datapusher
RUN chmod -R +x ~/venv/bin
RUN ~/venv/bin/pip install -qr ~/datapusher/requirements.txt

USER root

# Remove build-time deps
RUN apt-get remove -y libxml2-dev libxslt-dev libz-dev
