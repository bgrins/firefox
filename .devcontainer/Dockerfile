ARG DEBIAN_VERSION=bookworm
FROM debian:${DEBIAN_VERSION}

ARG TIMEZONE=Etc/UTC
ARG CLAUDE_CODE_VERSION=latest

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=${TIMEZONE}
ENV DEVCONTAINER=true
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    bash \
    bison \
    build-essential \
    cabextract \
    clang \
    cmake \
    curl \
    dnsutils \
    file \
    flex \
    gawk \
    git \
    gnupg \
    iproute2 \
    iptables \
    ipset \
    jq \
    less \
    libbz2-dev \
    libexpat1-dev \
    libffi-dev \
    libgtk-3-0 \
    libncursesw5-dev \
    libsqlite3-dev \
    libssl-dev \
    libtool \
    libucl-dev \
    libxml2-dev \
    lld \
    locales \
    make \
    man-db \
    mercurial \
    msitools \
    nano \
    ninja-build \
    nodejs \
    npm \
    openssh-client \
    p7zip-full \
    pkg-config \
    procps \
    python3 \
    python3-dev \
    python3-pip \
    python3-requests \
    python3-toml \
    rsync \
    scons \
    screen \
    subversion \
    sudo \
    tar \
    tmux \
    unzip \
    uuid \
    uuid-dev \
    vim \
    wget \
    zip \
    zlib1g-dev && \
    (apt-get install -y gcc-multilib || echo "gcc-multilib not available on this architecture") && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup target add aarch64-apple-darwin


RUN useradd -m -s /bin/bash -u 1000 dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/dev && \
    chmod 0440 /etc/sudoers.d/dev

RUN mkdir -p /commandhistory /home/dev/.mozbuild /home/dev/.cargo /home/dev/.rustup && \
    chown -R dev:dev /commandhistory /home/dev/.mozbuild /home/dev/.cargo /home/dev/.rustup && \
    touch /commandhistory/.bash_history && \
    chown dev:dev /commandhistory/.bash_history && \
    ln -s /commandhistory/.bash_history /home/dev/.bash_history

RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" && \
    mkdir -p /usr/local/share/npm-global && \
    chown -R dev:dev /usr/local/share/npm-global

COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh && \
    echo "dev ALL=(ALL) NOPASSWD: /usr/local/bin/init-firewall.sh" >> /etc/sudoers.d/firewall && \
    chmod 0440 /etc/sudoers.d/firewall

ENV EDITOR=nano
ENV PATH="/home/dev/.cargo/bin:${PATH}"

WORKDIR /workspace

USER dev
