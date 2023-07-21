FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .

RUN pip3 install pipenv
RUN pipenv requirements --hash > requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD uvicorn src.main:app --host 0.0.0.0 --port 80
