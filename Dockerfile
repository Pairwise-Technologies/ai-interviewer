FROM --platform=linux/amd64 ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update  \
    && apt-get install -y \
    build-essential \
    ca-certificates \
    cmake \
    gfortran \
    libopencv-dev \
    libdbus-1-3 \
    libgbm1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libglib2.0-dev \
    libssl-dev \
    libx11-dev \
    libx11-xcb1 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-xfixes0 \
    libxcb-xtest0 \
    libgl1-mesa-dri \
    libxfixes3 \
    linux-libc-dev \
    pkgconf

# Install ALSA
RUN apt-get install -y libasound2 libasound2-plugins alsa alsa-utils alsa-oss

# Install Pulseaudio
RUN apt-get install -y  pulseaudio pulseaudio-utils

# Install Linux Kernel Dev
RUN apt-get update && apt-get install -y linux-libc-dev

# Install Ctags
RUN apt-get update && apt-get install -y universal-ctags

# Copy requirements.txt first (for cache)
COPY requirements.txt .

# Install python dependencies through requirements
RUN pip install --no-cache-dir -r requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python

# CMD ["python", "launch.py"]

CMD ["/bin/bash"]