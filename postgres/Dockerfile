FROM postgres:latest

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD default
ENV POSTGRES_DB master

COPY postgresql.conf /etc/postgresql.conf
ADD setup.sql /docker-entrypoint-initdb.d/