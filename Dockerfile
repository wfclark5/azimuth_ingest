FROM python:3.8

COPY . /working 

RUN chmod 755 /working/source/ingest_val.py

WORKDIR /working

RUN pip install -r requirements.txt

CMD [ "python", "/working/source/ingest_val.py" ]