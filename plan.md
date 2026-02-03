# Planning document

This document contains what my current plans are for this project. This is changed as time goes on.

## Backend

The app is run in a docker container, and runs each server alongside itself, in `/servers/<uuid>`, with the executable being server.jar, and the entrypoint as start.sh

### Source code structure

- `/app` # Flask app, like html, css, and everything else.
- `/serverconfigs` # Server configurations
  - `/vanilla` # A vanilla server
    - `/create.sh` # Contains setup data, installs jre and downloads the vanilla server to server.jar to the server directory, also sets up the start.sh script
  - `/paper` # Another example
    - `/create.sh` # Installs jre, finds the latest paper release for a specific minecraft version, and downloads it

### First start

When the app is first started, you need to agree to the Minecraft EULA, then a velocity proxy (from /serverconfigs/proxy/create.sh) is created, started to generate config files, then shut down.

### Dependencies

- Flask
  - Used to serve the app
- Flask-SocketIO
  - Used for realtime logs and communication, could probably also provide api access somehow
- Flask-SQLAlchemy
  - Provides easy SQLite access for interacting with the DB like a python class

## Directories

The app will store data in /var/mcserv, including the db, which is /var/mcserv/data.sqlite3
There will be a user (mcserv) that will run the application, and should own the /var/mcserv directory and have read permission for /etc/mcserv.yml
Servers will be in /var/mcserv/servers/\<UUID\> and will be mounted to /server within server containers.