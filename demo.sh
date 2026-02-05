#!/bin/bash
if ! command -v git &> /dev/null
then
    echo "Please install git"
    exit 1
fi
if ! command -v docker &> /dev/null
then
    echo "Please install docker"
    exit 1
fi
git clone https://github.com/trwy7/minecraftmanager
cd minecraftmanager
cp .env.example .env
docker compose up --build