FROM --platform=linux/amd64 ubuntu:22.04 AS base

SHELL ["/bin/bash", "-c"]

ENV project=attendee_fastapi
ENV cwd=/$project

WORKDIR $cwd

ARG DEBIAN_FRONTEND=noninteractive

# Install Dependencies for Bot Automation
RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    gdb \
    git \
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
    pkgconf \
    python3-pip \
    tar \
    unzip \
    zip \
    vim \
    libpq-dev

# Install Chrome dependencies for Google Meet/Zoom automation
RUN apt-get install -y \
    xvfb \
    x11-xkb-utils \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-scalable \
    xfonts-cyrillic \
    x11-apps \
    libvulkan1 \
    fonts-liberation \
    xdg-utils \
    wget

# Install specific Chrome version for bot automation
RUN wget -q http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_134.0.6998.88-1_amd64.deb
RUN apt-get install -y ./google-chrome-stable_134.0.6998.88-1_amd64.deb

# Install ALSA for audio capture
RUN apt-get update && apt-get install -y \
    libasound2 \
    libasound2-plugins \
    alsa \
    alsa-utils \
    alsa-oss

# Install Pulseaudio and FFmpeg for audio processing
RUN apt-get install -y \
    pulseaudio \
    pulseaudio-utils \
    ffmpeg

# Install GStreamer for media processing
RUN apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgirepository1.0-dev \
    --fix-missing

# Install additional tools
RUN apt-get update && apt-get install -y \
    universal-ctags \
    xterm

# Alias python3 to python
RUN ln -s /usr/bin/python3 /usr/bin/python

FROM base AS deps

# Install Python dependencies
RUN pip install --upgrade pip

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python packages including FastAPI specific ones
RUN pip install -r requirements.txt

# Install additional Python packages for bot functionality
RUN pip install \
    pyjwt \
    cython \
    gdown \
    deepgram-sdk \
    python-dotenv \
    selenium \
    opencv-python \
    pydub \
    webrtcvad \
    google-api-python-client \
    google-auth \
    google-cloud-texttospeech \
    zoom-meeting-sdk \
    stripe \
    kubernetes \
    boto3 \
    django-storages

# Install Tini for proper signal handling
ENV TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

FROM deps AS build

WORKDIR $cwd

# Copy application code
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /opt/bin/entrypoint.sh
RUN chmod +x /opt/bin/entrypoint.sh

# Add root to pulse-access group for audio
RUN adduser root pulse-access

# Set Python path
ENV PYTHONPATH=/attendee_fastapi

# Expose port
EXPOSE 8000

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/tini", "--"]

# Default command
CMD ["/opt/bin/entrypoint.sh"]


