# start from base image
FROM python:3.8-buster

# put build number variable first to force new build every time
ARG BUILD_NUMBER_ARG
ENV BUILD_NUMBER ${BUILD_NUMBER_ARG}

# helper variable to let the app know its running inside docker
ENV IS_DOCKER TRUE

# database host
ARG DB_HOST_ARG
ENV DB_HOST ${DB_HOST_ARG}

# database username
ARG DB_USERNAME_ARG
ENV DB_USERNAME ${DB_USERNAME_ARG}

# database password
ARG DB_PASSWORD_ARG
ENV DB_PASSWORD ${DB_PASSWORD_ARG}

# set working directory
WORKDIR /app

# install pipenv, add Pipfiles, and install
RUN pip install pipenv
COPY Pipfile* /app/
RUN pipenv install --deploy

# add source code to /app folder
COPY /src /app

# run unit tests in container (hacky but easy)
COPY .coveragerc /app
RUN pipenv run nose2 --coverage . --with-coverage --log-level CRITICAL

# run pending DDL changes against database
# don't use "flask db upgrade", avoiding circular import errors
# disabled for now, as the DB will be built from a dump file on each update
#RUN pipenv run python modManage.py db upgrade

# start app
# don't use "flask run", avoiding circular import errors
CMD pipenv run python -u modApp.py
