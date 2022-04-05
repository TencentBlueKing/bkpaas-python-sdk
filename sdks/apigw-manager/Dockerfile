FROM python:3.7-slim-buster

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:/apigw-manager/demo/bin:$PATH"
RUN pip3 install --upgrade pip

COPY src /apigw-manager/src
COPY demo /apigw-manager/demo
COPY manage.py /apigw-manager/manage.py
COPY pyproject.toml /apigw-manager/pyproject.toml
COPY poetry.lock /apigw-manager/poetry.lock

WORKDIR /apigw-manager
RUN pip3 install .[demo]
RUN python manage.py migrate

WORKDIR /data

CMD ["sync-apigateway"]

ONBUILD ARG BK_APIGW_NAME
ONBUILD ENV BK_APIGW_NAME "${BK_APIGW_NAME}"

ONBUILD ARG BK_APP_CODE
ONBUILD ENV BK_APP_CODE "${BK_APP_CODE}"
