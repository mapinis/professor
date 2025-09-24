# Dockerfile for safe Claude bash execution
FROM alpine:latest

# Install basic tools that are commonly needed
RUN apk add --no-cache \
    bash \
    coreutils \
    curl \
    git \
    python3 \
    py3-pip \
    jq \
    tree \
    file \
    which \
    gcc \
    g++ \
    libc-dev \
    python3-dev

# Install some important python libraries
RUN pip install --break-system-packages \
    pandas \
    numpy \
    matplotlib \
    scipy

# Create a non-root user for extra safety
RUN adduser -D -s /bin/bash sandbox

# Create a workspace directory
RUN mkdir -p /workspace && chown sandbox:sandbox /workspace

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER sandbox

# Default command
CMD ["/bin/bash"]