FROM python:3.11-slim
LABEL maintainer="fragarie"
LABEL description="Protea.API"

# create user, venv and copy files
RUN useradd -ms /bin/bash protea
RUN python3 -m venv /home/protea/venv
COPY requirements.txt /home/protea
RUN /home/protea/venv/bin/pip3 install -r /home/protea/requirements.txt
COPY . /home/protea/
WORKDIR /home/protea
USER protea

ENTRYPOINT ["/home/protea/venv/bin/python3", "start.py"]