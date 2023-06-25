FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y ffmpeg python3 python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY frame_extraction.py .

CMD [ "python3", "frame_extraction.py" ]
