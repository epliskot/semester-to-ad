# FROM docker.nmbu.no:5000/remote/python:3-stretch
MAINTAINER Jon Dellnes "jon.dellnes@nmbu.no"

RUN mkdir /app /app/server
COPY requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

COPY server /app/server

# The deploy script will copy the contents of the image's "deployment" folder
# over to the designated linux server. When we build the image, we'll thus need to populate the folder
# with the required file(s). See https://confluence.nmbu.no/x/-4DwAQ for more info.
COPY docker-compose.production.yml scripts/run-production.sh /deployment/

RUN useradd -ms /bin/bash api-user
