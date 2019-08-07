FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y curl python3 python3-pip
# RUN curl --silent --location https://deb.nodesource.com/setup_6.x |  bash - && apt-get update && apt-get install -y nodejs npm

WORKDIR /usr/src/app

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt 

CMD [ "python3", "./app.py" ]
