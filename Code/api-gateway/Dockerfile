FROM python:3.7.9-slim-buster

RUN apt-get update 
RUN apt-get install -y python3-uvicorn
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./src/ .

RUN pip3 install -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "app.py"]
