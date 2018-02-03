FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD twote_requirements.txt /code/
 RUN pip install -r twote_requirements.txt
 ADD . /code/