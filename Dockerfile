FROM python:3.7

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN pip install --upgrade pip

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

COPY . .

RUN mkdir /app/static \
          /app/static/uploads \
          /app/static/uploads/current \
          /app/static/output \
          /app/static/output/reports \
          /app/static/logs \
          /app/static/zipped

RUN chmod -R 777 /app/static

COPY src /paws-data-pipeline/

RUN chmod 777 /paws-data-pipeline

WORKDIR /app/src

CMD python app.py


