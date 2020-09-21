FROM python:3.8-buster
RUN pip install pipenv
WORKDIR /app
COPY Pipfile* /app/
RUN pipenv install --deploy
COPY /src /app
ENV IS_DOCKER TRUE
COPY .coveragerc /app
RUN pipenv run nose2 --coverage . --with-coverage
CMD pipenv run python -u ./modApp.py
