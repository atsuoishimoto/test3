ARG BASEIMAGE=python:3.12.7-slim-bookworm

#--------------------------------------------------------------
FROM $BASEIMAGE AS install-poetry

# Setup Poetry

ENV PIP_CACHE_DIR=/var/pip/cache
ENV POETRY_HOME=/opt/poetry
ENV POETRY_CACHE_DIR=/var/poetry/cache

ADD https://install.python-poetry.org /tmp/poetry-install.py

RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    --mount=type=cache,target=${POETRY_CACHE_DIR} \
    python3 /tmp/poetry-install.py

#--------------------------------------------------------------
FROM $BASEIMAGE AS build

WORKDIR /opt/pythonenv/

# Setup build environment
RUN apt-get update
RUN apt-get install -y --no-install-recommends curl make gcc g++ libc-dev \
                    pkg-config libyaml-dev libffi-dev
# mysqlclient 使用時は以下をアンコメント \
# RUN apt-get install -y --no-install-recommends libmariadb-dev

ENV PIP_CACHE_DIR=/var/pip/cache
ENV POETRY_HOME=/opt/poetry
ENV POETRY_CACHE_DIR=/var/poetry/cache

COPY --from=install-poetry ${POETRY_HOME} ${POETRY_HOME}

ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN poetry config virtualenvs.in-project true

# Build packages
COPY pyproject.toml /opt/pythonenv/
COPY poetry.lock /opt/pythonenv/
RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    --mount=type=cache,target=${POETRY_CACHE_DIR} \
    poetry install --no-root --only main

#--------------------------------------------------------------
FROM $BASEIMAGE AS runtime

ARG TARGETARCH

# Install packages
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends libyaml-0-2 libffi8

# mysqlclient 使用時は以下をアンコメント \
# apt-get install -y --no-install-recommends libmariadb3

apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/* /var/tmp/* /root/.cache/*
EOF

# Setup account
RUN <<EOF
groupadd -g 999 appuser
useradd -r -u 999 -g appuser appuser
EOF

# Build directories
RUN <<EOF
mkdir -p /log
chown -R appuser:appuser /log
mkdir -p /usr/src/app
chown -R appuser:appuser /usr/src/app
mkdir -p /opt/pythonenv/
chown -R appuser:appuser /opt/pythonenv/
EOF

USER appuser

# Copy source files
WORKDIR /usr/src/app

COPY --chown=appuser:appuser . /usr/src/app
COPY --from=build /opt/pythonenv/.venv /opt/pythonenv/.venv

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/pythonenv/.venv/bin:${PATH}"
ENV PYTHONPATH=/usr/src/app/bbbb

RUN python -m manage collectstatic --noinput --settings=bbbb.settings.development

CMD ["uwsgi", "uwsgi.ini"]
