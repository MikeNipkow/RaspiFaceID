FROM python:3

RUN apt-get -y update

RUN apt-get install -y --fix-missing \
    cmake ffmpeg libsm6 libxext6

RUN useradd -rm -d /home/app -s /bin/bash -u 1001 app

WORKDIR /home/app

RUN whoami
USER app
RUN whoami

COPY --chown=app requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]
