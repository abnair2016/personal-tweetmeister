# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app

WORKDIR /code/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
