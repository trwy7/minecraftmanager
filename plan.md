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
- Flask-Migrate
  - Provides db migration features
  - TODO: See if I can make this automatic on container start
- Waitress
  - Serves the app

## Directories

The directories (as in the manager container) are:

- `/servers` # Contains server data and configurations
  - `/<ID>` # Per server data
    - `/server.jar` # Server jar file, should not be relied on existing, as some server softwares are not java. Instead, use run.sh to start the server
    - `/run.sh` # The entrypoint for a server
- `/data` # Contains manager configuration
  - `/db.sqlite3` # The app database

### Authentication

Authentication will be handled by OpenID. This allows login methods like google, discord, and many others. Because there are no permissions, on a user's first login, a code will be printed to console, and will need to be typed in.

### DB structure

- User
  - UUID
  - Name
- Server
  - ID
  - Type (one of proxy, lobby, or )

#### Server id structure

Each server ID follows the structure 30xxx, except for the proxy, which uses 25565.
The server ID is used as the server port. The 0 in each ID can be changed for plugin usage, e.x. server on port 30001, and vc on 31001.
