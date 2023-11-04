FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH /root/.local/bin:$PATH
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/
RUN poetry install
COPY /app /app/app

CMD ["sh", "-c", "set -e; export PYTHONPATH=/app; cd /app/app && uvicorn main:app --reload --host 0.0.0.0 --port 8080"]
