FROM --platform=linux/amd64 ubuntu:22.04 AS base

SHELL ["/bin/bash", "-c"]

ENV project=attendee_fastapi
ENV cwd=/$project

WORKDIR $cwd

ARG DEBIAN_FRONTEND=noninteractive

# Install Dependencies cho Bot Automation trong một layer
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
    libpq-dev \
    # Chrome dependencies
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
    wget \
    # ALSA for audio
    libasound2 \
    libasound2-plugins \
    alsa \
    alsa-utils \
    alsa-oss \
    # Pulseaudio and FFmpeg
    pulseaudio \
    pulseaudio-utils \
    ffmpeg \
    # GStreamer
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgirepository1.0-dev \
    # Additional tools
    universal-ctags \
    xterm \
    && wget -q http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_134.0.6998.88-1_amd64.deb \
    && apt-get install -y ./google-chrome-stable_134.0.6998.88-1_amd64.deb \
    && rm -f google-chrome-stable_134.0.6998.88-1_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

FROM base AS deps

# Upgrade pip
RUN pip install --upgrade pip --no-cache-dir

# Copy requirements first để tận dụng Docker cache
COPY requirements.txt .

# Install Python packages với --no-cache-dir để giảm kích thước
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
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

# Install Tini
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

# Add root to pulse-access group
RUN adduser root pulse-access

# Set Python path
ENV PYTHONPATH=/attendee_fastapi

# Expose port
EXPOSE 8000

# Use tini as entrypoint
ENTRYPOINT ["/tini", "--"]

# Default command
CMD ["/opt/bin/entrypoint.sh"]


