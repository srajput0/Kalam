# Use a Python 3.9.6 slim buster base image
FROM python:3.9.6-slim-buster

# Update and install dependencies using apt
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        musl-dev \
        ffmpeg \
        aria2 \
        make \
        g++ \
        cmake \
        wget \
        unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and build mp4decrypt from Bento4
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip && \
    unzip v1.6.0-639.zip && \
    cd Bento4-1.6.0-639 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    cp mp4decrypt /usr/local/bin/ && \
    cd ../.. && \
    rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# Copy all files into the container
COPY . /app/
WORKDIR /app/

# Python dependencies install
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --upgrade --requirement requirements.txt \
    && python3 -m pip install -U yt-dlp \
    && pip3 install pytube

# Set the command to run the application
CMD gunicorn app:app & python3 main000.py
