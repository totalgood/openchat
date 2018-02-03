FROM maven:latest
  RUN mkdir /code
  WORKDIR /code
  ADD . /code/
  RUN mvn dependency:copy-dependencies -DoutputDirectory=./jars
  RUN ls -lh

FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD twote_requirements.txt /code/
 RUN pip install -r twote_requirements.txt
 ADD . /code/
 COPY --from=0 /code/jars/ ./jars
 RUN ls -lh