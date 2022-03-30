FROM python:3.7-slim-buster

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --upgrade pip

COPY . /apigw-manager
WORKDIR /apigw-manager
RUN pip3 install .[demo]
RUN python manage.py migrate

CMD ["bash"]