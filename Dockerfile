FROM python:3.9.6-slim
RUN apt-get update -y  && pip install digi-xbee && pip3 install gpiozero && pip3 install redis && apt-get install redis-server -y
#WORKDIR /app
COPY ./app/ /app/
RUN mkdir config_host 
CMD [ "python3", "app/app.py" ]
