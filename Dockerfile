FROM python:3.9.6-slim
RUN apt-get update -y && pip install digi-xbee && pip3 install gpiozero
# WORKDIR /app
COPY ./app/ /app/
RUN mkdir config_host 
CMD [ "python3", "app/receive_frame.py" ]
