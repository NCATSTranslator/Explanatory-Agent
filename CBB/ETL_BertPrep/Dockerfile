FROM python:3.8-buster
RUN pip install pipenv
WORKDIR /app
COPY Pipfile* /app/
RUN pipenv install --deploy
RUN pipenv run python -c "import nltk; nltk.download('punkt')"
COPY /src /app
ENV IS_DOCKER TRUE
CMD ["pipenv", "run", "python", "-u", "./modMain.py"]