FROM python:3.10-slim-bullseye as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Poetry config
    POETRY_VERSION=1.2.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    # PIP config
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Path config (pysetup for storing Poetry toml/lock files)
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="$PYSETUP_PATH/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
   && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    && pip install --no-cache-dir --upgrade pip

FROM base as builder

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

FROM base as development
ENV WORK_ENV=development

COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
RUN poetry install

WORKDIR /app
COPY . .

EXPOSE 8000
CMD . /opt/pysetup/.venv/bin/activate && exec python3 auth/main.py
