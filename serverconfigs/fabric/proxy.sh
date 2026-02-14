#!/usr/bin/env bash

# Get forwarding secret from the proxy
if [ -f "/servers/25565/forwarding.secret" ]; then
  FORWARD_SECRET=$(cat /servers/25565/forwarding.secret)
else
  echo "Error: Can't find the proxy forwarding secret"
  exit 1
fi

# Create config/FabricProxy-Lite.toml
echo "Creating config/FabricProxy-Lite.toml..."
cat > config/FabricProxy-Lite.toml <<EOF
hackOnlineMode = false
hackEarlySend = true
hackMessageChain = true
secret = "$FORWARD_SECRET"
EOF