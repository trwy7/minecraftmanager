#!/bin/bash

echo "Fixing permissions..."
chown -R 1000:1000 /servers /data

echo "Starting user script..."
exec sudo -u appuser /app/entrypoint.user.sh $@