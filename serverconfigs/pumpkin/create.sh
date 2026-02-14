#!/usr/bin/env bash

curl -Lo server https://github.com/Pumpkin-MC/Pumpkin/releases/download/nightly/pumpkin-X64-Linux

chmod +x server

cat > run.sh <<EOF
#!/usr/bin/env sh
./server
EOF

chmod +x run.sh

mkdir -p config
RCON_PORT=$(($1 + 1000))
cat > config/configuration.toml <<EOF
java_edition_address = "0.0.0.0:$1"
bedrock_edition = false
EOF

cat > config/features.toml <<EOF
[networking.proxy]
enabled = true

[networking.proxy.velocity]
enabled = true
secret = ""

[networking.query]
enabled = true
address = "0.0.0.0:$1"

[networking.rcon]
enabled = true
address = "0.0.0.0:$RCON_PORT"
password = "mcmanager"
max_connections = 0
EOF

/app/serverconfigs/pumpkin/proxy.sh