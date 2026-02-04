#!/bin/bash

#echo "Applying db migrations..."
# Produces errors a lot, I might add this back at some point
#flask db upgrade

echo "Starting app..."
exec "$@"