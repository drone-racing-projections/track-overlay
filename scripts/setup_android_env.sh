#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
AVD_NAME="${AVD_NAME:-GateRace_API34}"
if ! command -v java >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq openjdk-17-jdk-headless wget unzip curl \
    libpulse0 libnss3 libxcomposite1 libxcursor1 libxi6 libxtst6 libasound2t64 libgl1 libglib2.0-0t64
fi
mkdir -p "$ANDROID_HOME/cmdline-tools"
if [ ! -x "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
  cd /tmp
  wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip
  rm -rf "$ANDROID_HOME/cmdline-tools/latest"
  unzip -q -o cmdline-tools.zip -d "$ANDROID_HOME/cmdline-tools"
  mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest"
fi
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator"
yes | sdkmanager --licenses >/tmp/sdk-licenses.log 2>&1 || true
sdkmanager --install "platform-tools" "platforms;android-34" "build-tools;34.0.0" "emulator" \
  "system-images;android-34;google_apis;x86_64"
echo no | avdmanager create avd -n "$AVD_NAME" -k "system-images;android-34;google_apis;x86_64" -d pixel_6 --force
echo "ANDROID_HOME=$ANDROID_HOME AVD=$AVD_NAME"
