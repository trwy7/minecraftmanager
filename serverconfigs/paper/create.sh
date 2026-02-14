#!/usr/bin/env bash

# Taken from https://docs.papermc.io/misc/downloads-service/

PROJECT="paper"
MINECRAFT_VERSION="$2"
USER_AGENT="mcmanage (https://github.com/trwy7/minecraftmanager)"

# First check if the requested version has a stable build
BUILDS_RESPONSE=$(curl -s -H "User-Agent: $USER_AGENT" https://fill.papermc.io/v3/projects/${PROJECT}/versions/${MINECRAFT_VERSION}/builds)

# Check if the API returned an error
if echo "$BUILDS_RESPONSE" | jq -e '.ok == false' > /dev/null 2>&1; then
  ERROR_MSG=$(echo "$BUILDS_RESPONSE" | jq -r '.message // "Unknown error"')
  echo "Error: $ERROR_MSG"
  exit 1
fi

# Try to get a stable build URL for the requested version
PAPERMC_URL=$(echo "$BUILDS_RESPONSE" | jq -r 'first(.[] | select(.channel == "STABLE") | .downloads."server:default".url) // "null"')
FOUND_VERSION="$MINECRAFT_VERSION"

# If no stable build for requested version, find the latest version with a stable build
if [ "$PAPERMC_URL" == "null" ]; then
  echo "No stable build for version $MINECRAFT_VERSION, searching for latest version with stable build..."

  # Get all versions for the project (using the same endpoint structure as the "Getting the latest version" example)
  # The versions are organized by version group, so we need to extract all versions from all groups
  # Then sort them properly as semantic versions (newest first)
  VERSIONS=$(curl -s -H "User-Agent: $USER_AGENT" https://fill.papermc.io/v3/projects/${PROJECT} | \
    jq -r '.versions | to_entries[] | .value[]' | \
    sort -V -r)

  # Iterate through versions to find one with a stable build
  for VERSION in $VERSIONS; do
    VERSION_BUILDS=$(curl -s -H "User-Agent: $USER_AGENT" https://fill.papermc.io/v3/projects/${PROJECT}/versions/${VERSION}/builds)

    # Check if this version has a stable build
    STABLE_URL=$(echo "$VERSION_BUILDS" | jq -r 'first(.[] | select(.channel == "STABLE") | .downloads."server:default".url) // "null"')

    if [ "$STABLE_URL" != "null" ]; then
      PAPERMC_URL="$STABLE_URL"
      FOUND_VERSION="$VERSION"
      echo "Found stable build for version $VERSION"
      break
    fi
  done
fi

if [ "$PAPERMC_URL" != "null" ]; then
  # Download the latest Paper version
  curl -o server.jar $PAPERMC_URL
  echo "Download completed (version: $FOUND_VERSION)"
else
  echo "No stable builds available for any version :("
  exit 1
fi
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
#server-ip=127.0.0.1

/app/serverconfigs/paper/proxy.sh

# Install plugins
echo "Installing plugins..."
mkdir -p plugins/voicechat
/app/serverconfigs/modrinthdownload.sh "luckperms" "paper" "$MINECRAFT_VERSION" "plugins/luckperms.jar"
/app/serverconfigs/modrinthdownload.sh "simple-voice-chat" "paper" "$MINECRAFT_VERSION" "plugins/simple-voice-chat.jar"
/app/serverconfigs/modrinthdownload.sh "viaversion" "paper" "$MINECRAFT_VERSION" "plugins/viaversion.jar"
/app/serverconfigs/modrinthdownload.sh "viabackwards" "paper" "$MINECRAFT_VERSION" "plugins/viabackwards.jar"
/app/serverconfigs/modrinthdownload.sh "viarewind" "paper" "$MINECRAFT_VERSION" "plugins/viarewind.jar"
curl -o plugins/floodgate.jar -LH "User-Agent: $USER_AGENT" https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/spigot

# Create voicechat config
VOICE_PORT=$(($1 + 100))
echo "port=$VOICE_PORT" > plugins/voicechat/voicechat-server.properties

# Create run.sh
echo "Creating run.sh..."
# Get correct java version
JAVA_VERSION=""
if [ -n "$MINECRAFT_VERSION" ]; then
  if [[ "$MINECRAFT_VERSION" =~ ^([0-9]+)(\.([0-9]+))? ]]; then
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
java$JAVA_VERSION -Xms1024M -Xmx2048M -jar server.jar nogui
EOF
chmod +x run.sh