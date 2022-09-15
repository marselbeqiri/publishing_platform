FROM python:3-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update

# Making app as the working directory and copying it to docker
RUN mkdir /app
RUN mkdir /app/static
WORKDIR /app
COPY . /app/

# Install all dependencies
COPY requirements.txt /app/requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev libffi-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

CMD ["sh", "shell_scripts/start_django.sh"]
