FROM python:3.10-slim

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

WORKDIR /app/

COPY . /app

RUN pip3 install -r requirements.txt





