#!/usr/bin/env bash

PROJECT="$1"
LOADER="$2"
MINECRAFT_VERSION="$3"
SAVE_LOCATION="$4"
USER_AGENT="mcmanage (https://github.com/trwy7/minecraftmanager)"

# I wish I could make this look nicer
API_URL="https://api.modrinth.com/v2/project/$PROJECT/version?loaders=%5B%22$LOADER%22%5D&game_versions=%5B%27$MINECRAFT_VERSION%27%5D&include_changelog=false"
VERSION=$(curl -s -H "User-Agent: $USER_AGENT" "$API_URL" | jq -r '.[0].files[0].url // empty')
if [ -z "$VERSION" ]; then
  echo "No version found for project $PROJECT with loader $LOADER and Minecraft version $MINECRAFT_VERSION"
  exit 1
fi
echo "Downloading $PROJECT version for Minecraft $MINECRAFT_VERSION with loader $LOADER..."
echo "Download URL: $VERSION"
curl -L -o "$SAVE_LOCATION" "$VERSION"