FROM python:3.6

WORKDIR /app

COPY ./src/ .

RUN pip3 install -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python3", "app.py"]
