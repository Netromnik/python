FROM python:3.8-alpine AS test2
RUN mkdir /code/
WORKDIR /code
COPY req.txt .
RUN python3.8 -m venv /code/venv 
ENV PATH="/code/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install gunicorn
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 python3 -m pip install -r req.txt --no-cache-dir && \
 apk --purge del .build-deps

# copy project
FROM python:3.8-alpine AS product
RUN apk update
RUN apk add libmagic
ENV PYTHONUNBUFFERED 1
ENV LDAP_HOST localhost
ENV LDAP_PORT 9000
ENV PATH="/code/venv/bin:$PATH" 
RUN mkdir  /code /web /web/media /web/static /web/log
COPY --from=test2 /code/venv /code/venv
RUN apk add --no-cache python3 postgresql-libs
WORKDIR /code
EXPOSE 8000
COPY . /code
RUN python3.8 /code/manage.py collectstatic --no-input
CMD gunicorn helpdesk.wsgi --bind 0.0.0.0:8000
