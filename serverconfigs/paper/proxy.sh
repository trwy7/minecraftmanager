#!/usr/bin/env bash

# Get forwarding secret from the proxy
if [ -f "/servers/25565/forwarding.secret" ]; then
  FORWARD_SECRET=$(cat /servers/25565/forwarding.secret)
else
  echo "Error: Can't find the proxy forwarding secret"
  exit 1
fi

# Create config/paper-global.yml
echo "Creating config/paper-global.yml..."
mkdir -p config
cat > config/paper-global.yml <<EOF
# Auto generated paper-global.yml
proxies:
  velocity:
    enabled: true
    online-mode: true
    secret: '$FORWARD_SECRET'
EOF

mkdir -p plugins/floodgate
cp /servers/25565/plugins/floodgate/key.pem plugins/floodgate/key.pem