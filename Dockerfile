FROM python:3-bookworm
LABEL org.opencontainers.image.authors Victor Seva <linuxmaniac@torreviejawireless.org>

WORKDIR /project
VOLUME /etc/kamcli

COPY . .
RUN pip3 install .
RUN pip3 install psycopg2 mysqlclient
