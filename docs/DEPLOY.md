# Deploying the server

This guide runs the authoritative Asteroids server on a Linux VPS as a
`systemd` service: in the background, restarting on crash, surviving
reboots and SSH logout, with logs in the journal.

It covers the **server** only. The game client is a native pygame
program each player runs on their own machine — see the
[README](../README.md) for how to launch it against a remote `--host`.

> The server is headless, pure Python. It imports neither pygame nor any
> display/SDL library, so the VPS needs no graphics stack — only Python
> and the `websockets` package.

## Prerequisites

- A Linux VPS with root access (examples use **Ubuntu 24.04 LTS**).
- The TCP port you want to serve on (default `8765`) reachable from the
  internet. On Ubuntu this is controlled by `ufw`; some providers add a
  second firewall in their control panel — make sure **both** allow the
  port.

## Setup

These steps need root. If direct root login over SSH is disabled
(recommended), become root from your admin user with `sudo -i` — it
asks your password — or use the provider's web terminal, which logs in
as root. Run the commands below as root.

### 1. System packages

```bash
apt update && apt install -y python3-venv git
```

### 2. A dedicated service user

Running a network service as `root` is needless risk. Create an
unprivileged system user that owns the install and runs the process:

```bash
adduser --system --group --home /opt/asteroids_multiplayer asteroids
```

### 3. The code

```bash
git clone https://github.com/jucimarjr/asteroids_multiplayer /opt/asteroids_multiplayer
cd /opt/asteroids_multiplayer
```

(If the repository is private, clone over SSH with a deploy key or use a
personal access token.)

### 4. A virtualenv with server-only dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install -r deploy/requirements-server.txt
```

This installs only `websockets`. Do **not** run `pip install -e .`
here — that pulls in pygame, which the server never uses.

### 5. The token allowlist

Every client must present a token from an allowlist the server reads at
boot (`server/auth.py`). Generate one token per student — one per line,
`#` comments and blank lines ignored — into `tokens.txt`:

```bash
.venv/bin/python -c "import secrets; [print(secrets.token_urlsafe(8)) for _ in range(30)]" > tokens.txt
chmod 600 tokens.txt
```

Adjust the `range(30)` to your class size. Hand each student one token;
the same token may be reused across reconnects. Then give the install to
the service user:

```bash
chown -R asteroids:asteroids /opt/asteroids_multiplayer
```

### 6. Size the rooms

Each room holds up to 8 players (`MAX_PLAYERS` in `core/config.py`). Set
`--rooms` to ceil(students / 8) — a class of ~30 needs `--rooms 4`.
Players choose their room with the client's `--room <id>` flag (`0` to
`N-1`). To change the count later you restart the server; there is no
runtime room creation.

### 7. Install and start the service

The unit file ships in `deploy/asteroids-server.service`. Edit `--rooms`
and `--port` in its `ExecStart` line if the defaults (4 rooms, port
8765) don't fit, then install it:

```bash
cp deploy/asteroids-server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now asteroids-server
```

`enable --now` starts it immediately and on every boot.
`Restart=on-failure` brings it back if the process ever crashes — which
matters because the whole simulation is a single event loop, so one
unhandled error would otherwise take every room down at once.

### 8. Open the firewall

```bash
ufw allow OpenSSH
ufw allow 8765/tcp
ufw --force enable
```

## Verify

```bash
# Service is up and listening
systemctl status asteroids-server --no-pager
journalctl -u asteroids-server -n 20 --no-pager
# expect: asteroids server listening on ws://0.0.0.0:8765

# Port reachable from another machine
nc -vz <VPS_IP> 8765

# It restarts after a crash
systemctl kill -s SIGKILL asteroids-server
systemctl status asteroids-server --no-pager   # back to active (running)
```

End to end, from a machine that has the client installed:

```bash
python -m multiplayer.player --host <VPS_IP> --port 8765 --token <TOKEN> --room 0 --name test
```

A match starts once two players are connected to the same room; the
server logs `match started: room=0`.

## Day-to-day operation

Run these on the server as root — prefix each with `sudo` (or from a
`sudo -i` shell).

| Task | Command |
|---|---|
| Watch live logs / match events | `journalctl -u asteroids-server -f` |
| Change the number of rooms | edit `--rooms` in the unit, then `systemctl daemon-reload && systemctl restart asteroids-server` |
| Add or revoke tokens | edit `tokens.txt`, then `systemctl restart asteroids-server` (the allowlist is read at boot) |
| Update to the latest code | `git pull` in the install dir, then `systemctl restart asteroids-server` |
| Stop / start (e.g. only during class) | `systemctl stop asteroids-server` / `systemctl start asteroids-server` |

## Security notes and limitations

- **No TLS.** Clients connect over `ws://`, so the token travels in clear
  text and the high port can be blocked on school or office networks.
  For public-internet use, terminate TLS (`wss://`) on port 443 with a
  reverse proxy and a certificate — the VPS hostname works as the domain.
  That is a separate change (the client currently hardcodes `ws://`).
- **No rate limiting.** Any host that reaches the port can open
  connections; only a valid token lets one into a room. A simple
  mitigation is to keep the service stopped outside class hours.
