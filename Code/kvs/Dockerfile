FROM python:3.7.9-slim-buster

RUN apt-get update
RUN apt-get install -y python3-uvicorn
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./src/* /app/

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

CMD ["python3", "app.py"]
