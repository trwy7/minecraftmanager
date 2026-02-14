#!/usr/bin/env bash

USER_AGENT="mcmanage (https://github.com/trwy7/minecraftmanager)"

# Get the latest fabric server version

LOADER_VERSION=$(curl -s -H "User-Agent: $USER_AGENT" https://meta.fabricmc.net/v2/versions/loader | jq -r 'first(.[] | select(.stable == true) | .version)')
INSTALLER_VERSION=$(curl -s -H "User-Agent: $USER_AGENT" https://meta.fabricmc.net/v2/versions/installer | jq -r 'first(.[] | select(.stable == true)).version')
curl -Lo server.jar https://meta.fabricmc.net/v2/versions/loader/$2/$LOADER_VERSION/$INSTALLER_VERSION/server/jar
echo "eula=true" > eula.txt
# Create server.properties
echo "Creating server.properties..."
RCON_PORT=$(($1 + 1000))
cat > server.properties <<EOF
# Auto generated server.properties
query.port=$1
enable-query=true
server-port=$1
enable-rcon=true
rcon.port=$RCON_PORT
rcon.password=mcmanager
enforce-secure-profile=false
online-mode=false
EOF


# Install mods
echo "Installing mods..."
mkdir -p mods
/app/serverconfigs/modrinthdownload.sh "luckperms" "fabric" "$2" "mods/luckperms.jar"
/app/serverconfigs/modrinthdownload.sh "simple-voice-chat" "fabric" "$2" "mods/simple-voice-chat.jar"
/app/serverconfigs/modrinthdownload.sh "fabricproxy-lite" "fabric" "$2" "mods/fabricproxy-lite.jar"

# Create voicechat config
VOICE_PORT=$(($1 + 100))
mkdir -p config/voicechat
echo "port=$VOICE_PORT" > config/voicechat/voicechat-server.properties

# Proxy
/app/serverconfigs/fabric/proxy.sh

# Create run.sh
echo "Creating run.sh..."
# Get correct java version
JAVA_VERSION=""
if [ -n "2" ]; then
  if [[ "$2" =~ ^([0-9]+)(\.([0-9]+))? ]]; then
    MAJOR=${BASH_REMATCH[1]}
    MINOR=${BASH_REMATCH[3]:-0}
    if [ "$MAJOR" -eq 1 ] && [ "$MINOR" -lt 17 ]; then
      JAVA_VERSION="8"
    else
      JAVA_VERSION="21"
    fi
  else
    JAVA_VERSION="21"
  fi
fi
cat > run.sh <<EOF
#!/usr/bin/env sh
java$JAVA_VERSION -XX:+UseConcMarkSweepGC -XX:+UseParNewGC -XX:+CMSIncrementalPacing -XX:ParallelGCThreads=7 -XX:+AggressiveOpts -XX:+IgnoreUnrecognizedVMOptions -Xms1024M -Xmx2048M -jar server.jar nogui
EOF
chmod +x run.sh