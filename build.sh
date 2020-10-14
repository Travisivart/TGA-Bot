#!/usr/bin/env sh

ALPINE_BUILD_PKGS="--virtual .voice-build-deps build-base libffi-dev libsodium-dev musl-dev"
ALPINE_REQUIRED_PKGS="libffi libsodium opus-dev git ffmpeg gcc python3 python3-dev"

DEBIAN_BUILD_PKGS="build-essential libffi-dev libsodium-dev musl-dev"
DEBIAN_REQUIRED_PKGS="libffi7 libsodium23 libopus-dev git ffmpeg gcc python3 python3-dev python3-virtualenv"

LOG_DIR="/var/log/discordbot"
SYSTEM=$(grep ID= /etc/os-release | grep -v "\"" | awk -F '=' '{print $2}')
VENV="venv"

install_TGABot(){
  if [ ! -d "$VENV" ]; then
    echo Creating Virtual Environment
    virtualenv -p python3 "$VENV"
  fi

  . venv/bin/activate

  pip3 install -r requirements.txt

  chown -R "$SUDO_USER" "$VENV"

  # Create the logs directory
  mkdir $LOG_DIR
  chown -R "$SUDO_USER" "$LOG_DIR"
}

install_alpine(){
  apk update
  apk add $ALPINE_BUILD_PKGS
  apk add $ALPINE_REQUIRED_PKGS

  # Install python/pip
  ln -sf python3 /usr/bin/python
  python -m ensurepip

  # Install the Bot
  install_TGABot
  
  # Delete unneeded files
  apk del .voice-build-deps
}

install_debian(){
  apt update
  apt install -y $DEBIAN_BUILD_PKGS
  apt install -y $DEBIAN_REQUIRED_PKGS
  ln -sf python3 /usr/bin/python
  python -m ensurepip

  # Install the Bot
  install_TGABot

  apt remove -y $DEBIAN_BUILD_PKGS
}

if [ "$SYSTEM" = "alpine" ]; then
  install_alpine
else
  install_debian
fi

# If config.yaml does not exist, generate basic config.yaml
CONFIG="config.yaml"
if [ ! -f $CONFIG ]; then
  cp defaults.yaml "$CONFIG"
else
  echo "Your $CONFIG already exists, skipping generation of default $CONFIG."
fi
