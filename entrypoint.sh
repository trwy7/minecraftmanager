#!/bin/bash

echo "Applying db migrations..."
flask db upgrade

echo "Starting app..."
exec "$@"