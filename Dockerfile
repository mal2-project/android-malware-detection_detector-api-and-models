# #FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
FROM tiangolo/uvicorn-gunicorn-fastapi

# FROM nvidia/cuda:base


WORKDIR /app


COPY /requirements.txt /app
RUN apt-get update && apt-get -y install curl  && apt-get clean
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install -r requirements.txt

EXPOSE 80

COPY ./app /app

ENV DB_NAME=bincache
ENV DB_USER=bincache
ENV DB_PASSWORD=bincache
ENV DB_HOST=nanu
ENV PYTHON_PATH="/app"
