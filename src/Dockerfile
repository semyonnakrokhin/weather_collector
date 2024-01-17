# pull official base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/
ENV APP_HOME=/home/app

# create directory for the app user
RUN mkdir -p $HOME
# and then create the app user
RUN addgroup --system app && adduser --system --ingroup app app

# create authorized directory for app user and make it as workdir
RUN mkdir $APP_HOME
RUN mkdir $HOME/output_text
RUN mkdir $HOME/output_json
WORKDIR $APP_HOME

# install dependencies for linux
RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev

# copy environment
COPY ./../.env $HOME
COPY ./../alembic.ini $HOME

# install dependencies for python
COPY ./requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . .

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

ENTRYPOINT alembic upgrade head && python $APP_HOME/main.py
