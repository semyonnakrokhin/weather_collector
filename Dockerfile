#################################################################
####################### BUILD STAGE #############################
#################################################################
FROM python:3.10-slim

# Set PYTHONDONTWRITEBYTECODE to 1 to prevent Python from creating .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
# Set PYTHONUNBUFFERED to 1 to disable output buffering by Python,
# improving log readability.
ENV PYTHONUNBUFFERED 1


ENV ROOT_DIR=/home/my_project
ENV APP_DIR=/home/my_project/my_app


# create directory for the app user
RUN mkdir $ROOT_DIR
# and then create the app user
RUN addgroup --system app && adduser --system --ingroup app app


# create authorized directory for app user and make it as workdir
RUN mkdir $APP_DIR
WORKDIR $APP_DIR


# install dependencies for linux
RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev


##################################################################
######################### FINAL STAGE ############################
##################################################################


# install dependencies for python
COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt


COPY ./logs/ ./logs/
COPY ./src/ ./src/
COPY ./tests/ ./tests/
COPY ./alembic.ini ./alembic.ini
COPY ./config.ini ./config.ini
COPY ./logging.yaml ./logging.yaml
COPY ./pytest.ini ./pytest.ini


# chown all the files to the app user
RUN chown -R app:app $APP_DIR


# change to the app user
USER app
