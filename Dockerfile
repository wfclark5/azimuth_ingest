FROM python:3.8

ADD . /source

WORKDIR /source

RUN pip install -r requirements.txt

CMD [ "python", "/ingest_val.py" ]