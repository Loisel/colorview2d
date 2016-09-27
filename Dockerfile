FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
python \
python-pip \
python-scipy \
python-matplotlib \
ipython

RUN pip install PyYAML
RUN pip install --pre --upgrade --no-cache-dir colorview2d==0.6.post3
