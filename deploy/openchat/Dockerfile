#FROM maven:latest
#  RUN apt-get update \
#  && apt-get install -y python3 python-pip \
#  && apt-get clean
#
#  RUN python3 -V
#  RUN pip -V
#
#  RUN mkdir /code
#  WORKDIR /code
#  ADD . /code/
#  RUN mvn dependency:copy-dependencies -DoutputDirectory=./jars
#  RUN ls -lh
#
#  ENV PYTHONUNBUFFERED 1
#  ADD twote_requirements.txt /code/
#
#  RUN pip install -r twote_requirements.txt

FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD twote_requirements.txt /code/
 RUN pip install -r twote_requirements.txt
 ADD . /code/
 # COPY --from=0 /code/jars/ ./jars
 RUN ls -lh