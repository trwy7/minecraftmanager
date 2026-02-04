# Planning document

This document contains what my current plans are for this project. This is changed as time goes on.

## Backend

The app is run in a docker container, and runs each server alongside itself, in `/servers/<uuid>`, with the executable being server.jar, and the entrypoint as start.sh

### Source code structure

- `/app` # Flask app, like html, css, and everything else.
- `/serverconfigs` # Server configurations
  - `/vanilla` # A vanilla server
    - `/create.sh` # Contains setup data, downloads the vanilla server to server.jar to the server directory, also sets up the start.sh script
  - `/paper` # Another example
    - `/create.sh` # Finds the latest paper release for a specific minecraft version, and downloads it

### Server creation

`/create.sh` may use other server directories to generate it's own, some plugins require configuration from the proxy, which is available at /servers/25565 in the container.

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
- Requests
  - Download server software
- mcstatus
  - Get the player count of a server
- pyjwt
  - Gives auth tokens to users
- flask-bcrypt
  - Password hash provider
- flask-limiter
  - Rate limiter

## Directories

The directories (as in the manager container) are:

- `/servers` # Contains server data and configurations
  - `/<ID>` # Per server data
    - `/server.jar` # Server jar file, should not be relied on existing, as some server softwares are not java. Instead, use run.sh to start the server
    - `/run.sh` # The entrypoint for a server
- `/data` # Contains manager configuration
  - `/db.sqlite3` # The app database

### Authentication

The user will be given a jwt token to use for authentication.
Passwords are hashed with bcrypt.
When a user wants to sign up, we print a message in console, rate limited to 2 per hour across the whole app. If the user can get a code from the console, they are allowed to make their account, if 3 failed attempts happen, a new code must be made

### DB structure

- User
  - UUID
  - Name
- Server
  - ID
  - Name
  - Stop command
  - Type (one of proxy, lobby, or game)

#### Server id structure

Each server ID follows the structure 30xxx, except for the proxy, which uses 25565.
The server ID is used as the server port. The 0 in each ID can be changed for plugin usage, e.x. server on port 30001, and vc on 31001.
