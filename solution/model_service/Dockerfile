FROM python:3.10-slim

WORKDIR /model_service

COPY . /model_service/
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install -r requirements.txt

CMD python app.py
