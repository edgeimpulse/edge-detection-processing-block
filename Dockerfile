# syntax = docker/dockerfile:experimental
FROM python:3.7.5-stretch

WORKDIR /app

RUN apt update && apt install -y ffmpeg libsm6 libxext6

# Python dependencies
COPY requirements-blocks.txt ./
RUN pip3 --no-cache-dir install -r requirements-blocks.txt

COPY third_party /third_party
COPY . ./

EXPOSE 4446

CMD python3 -u dsp-server.py
