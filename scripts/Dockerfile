# Alpine Linux based image
FROM python:3.10-slim-bullseye
# See input and ouput unbuffered
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update 

RUN apt-get install -y  \
	vim
#    apt-get install -y \ 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . /app


CMD ["sh"]
