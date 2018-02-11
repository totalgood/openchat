FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD twote_requirements.txt /code/
 RUN pip install -r twote_requirements.txt
 ADD . /code/
 RUN echo "deb http://http.debian.net/debian jessie-backports main" | \
      tee --append /etc/apt/sources.list.d/jessie-backports.list > /dev/null
 RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y -t jessie-backports openjdk-8-jdk
# RUN update-java-alternatives -s java-1.8.0-openjdk-amd64