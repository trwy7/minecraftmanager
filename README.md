# Simple Minecraft Manager

Simple Minecraft Manager is a server manager for Minecraft. This is designed from the ground up to be as simple to set up as possible. This is designed for use with a friend group that requires more than one server, but still wants an easy to use solution.

## Requirements

The java minecraft server has high memory requirements. By default, 6 GB of ram is required for the proxy and papermc lobby, but increases with plugins/mods/quantity of servers.

## How to use

When starting your server for the first time, check the console for `Created initial 'admin' user with password`, and log in at localhost:7843 (or whatever your port is set to).
By default, a proxy and a lobby (papermc) server is created. These servers cannot be deleted, but new servers may be added very easily:

- Click add server
- Select a name, server software, and game version
- Wait 1 minute
- Add plugins
- Start your server
- Players may join with `/server <name>`, no restart needed

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
