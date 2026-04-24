# Simple Minecraft Manager

Simple Minecraft Manager is a server manager for Minecraft. This is designed from the ground up to be as simple to set up as possible. This is built for people who have little experience running a server. You may want to use [Crafty Controller](https://craftycontrol.com/) (Simple) or [Pterodactyl](https://pterodactyl.io/) (More features) if you have more experience.

## Features

- Automatic server setup
- Automatic velocity proxy configuration
- Easy to use
- Simple setup
- Multiple server support
- Easy server management

## Requirements

The java minecraft server has high memory requirements. By default, 4 GB of ram is required for the proxy and papermc lobby, but increases with plugins/mods/quantity of servers.
You must also agree to the [Minecraft EULA](https://aka.ms/MinecraftEULA)

## How to use

To run, you must install docker, you can learn how at https://docs.docker.com/engine/install/

## Quick setup

Run 

```sh
docker run -p 7843:7843 -p 25565:25565 -p 25565:25565/udp -p 19132:19132/udp -v mcm_servers:/servers -v mcm_data:/data -h minecraftmanager --stop-signal SIGINT --stop-timeout 60 ghcr.io/trwy7/minecraftmanager:1.0.0
```

then wait 1-2 minutes (depending on your internet connection and computer speed) and go to localhost:7843 in your browser. In your console, you should see `Created initial 'admin' user with password`, and log in with the password it gives you
## Full setup

This setup requires docker-compose, you can install it here: https://docs.docker.com/compose/install/linux/
Create this file in any directory as `docker-compose.yml`:

```yml
services:
  minecraftmanager:
    ports:
      - 7843:7843 # HTTP
      - 25565:25565 # Minecraft
      - 25565:25565/udp # Minecraft
      - 19132:19132/udp # Bedrock/Geyser
    volumes:
      - servers:/servers
      - data:/data
    environment:
      - SECRET_KEY=ChangeMeP13aseThisIsNotAGoodSecretKey
      - BASE_DOMAIN=mc.example.com # Optional
      - SERVER_OWNER=069a79f4-44e9-4726-a5be-fca90e38aaf5 # Optional
    hostname: minecraftmanager
    stop_signal: SIGINT
    stop_grace_period: 60s
    image: ghcr.io/trwy7/minecraftmanager:1.0.0
volumes:
  servers:
  data:
```

Replace `ChangeMeP13aseThisIsNotAGoodSecretKey` with any alphanumeric string larger than 32 characters
Replace `mc.example.com` with the domain that players can join from, this assumes you have a wildcard of your domain (`*.domain.tld`) that is also pointed at this server, you may remove this line if you do not have a domain you would like to use.
Replace `069a79f4-44e9-4726-a5be-fca90e38aaf5` with your own Minecraft UUID, or remove it
Finally, run `docker-compose up -d`
When starting your server for the first time, run `docker compose logs | grep password` to find the admin account password

## First run

When starting your server for the first time, check the console for `Created initial 'admin' user with password`, and log in at localhost:7843
By default, a proxy and a lobby (papermc) server is created. These servers cannot be deleted, but new servers may be added very easily:

- Click add server
- Select a name, server software, and game version
- Wait 1 minute
- Click your server's name
- Go to files
- Add some plugins/mods
- Start your server
- Players may join with `/server <name>` while in game, or by joining `<name>.<yourdomain>`

This project is designed to be forked, and for the user to add their own configurations.

## Included plugins

A list of each bundled plugin

- [Geyser + Floodgate](https://geysermc.org/)
  - Allows bedrock players to join your server(s)
- [Luckperms](https://luckperms.net/)
  - Automatically gives you the `*` permission on each server you create
- [Simple voice chat](https://modrinth.com/plugin/simple-voice-chat)
  - Proximity chat for minecraft
- [Velocitab](https://modrinth.com/plugin/velocitab)
  - Customizes the tab list
- [Velocircon](https://modrinth.com/plugin/velocircon)
  - RCON support for velocity
- [Viaversion](https://modrinth.com/plugin/viaversion) + [Viabackwards](https://modrinth.com/plugin/viabackwards) + [Viarewind](https://modrinth.com/plugin/viarewind)
  - Allows players from different client versions to join your server
- [FabricProxy-Lite](https://modrinth.com/mod/fabricproxy-lite)
  - Velocity forwarding support for fabric
