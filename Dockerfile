# postgres image with `pgvector` enabled
FROM postgres:16.3

RUN apt-get update \
    && apt-get install -y postgresql-server-dev-all build-essential \
    && apt-get install -y git \
    && git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && apt-get remove -y git build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5432
