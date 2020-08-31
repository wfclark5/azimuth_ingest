FROM python:3.8

ADD source/my_script.py 

RUN pip install -r requirements.txt

CMD [ "python", "./source/my_script.py" ]