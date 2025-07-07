FROM python:3.11

WORKDIR /app

COPY pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-root

COPY . .


ENV PYTHONPATH=/app/src

CMD ["uvicorn", "hello_api.routes:app", "--host", "0.0.0.0", "--port", "2005"]

