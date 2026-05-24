"""Tests covering the server-side handling of spectator connections.

The spectator client itself spawns pygame, which is hard to test
headlessly in CI. The interesting contracts are server-side:

- handshake parses the `spectator: true` flag;
- spectator is tracked in `Server.spectator_pids`;
- no ship spawned for spectators;
- spectators do not count toward `room_full` cap;
- INPUT and RESTART_REQUEST from spectators are silently dropped.
"""

from __future__ import annotations

import asyncio
import json

from core import config as C
from server.main import Server
from tests.test_server_room_registry import (
    VALID_TOKEN,
    FakeWebSocket,
    _hello,
)


def _spectator_hello(room_id: int = 0) -> str:
    return _hello(
        name="cam",
        room_id=room_id,
        spectator=True,
    )


def test_handshake_returns_spectator_flag_true():
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    ws = FakeWebSocket([_spectator_hello(0)])

    result = asyncio.run(server._handshake(ws))

    assert result is not None
    _, _, _, is_spectator = result
    assert is_spectator is True


def test_handshake_defaults_spectator_flag_false():
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    ws = FakeWebSocket([_hello(name="player")])

    result = asyncio.run(server._handshake(ws))

    assert result is not None
    _, _, _, is_spectator = result
    assert is_spectator is False


def test_spectator_does_not_count_toward_room_full_cap():
    """Saturate room 0 with players, then ensure a spectator HELLO
    still gets a WELCOME."""
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    # Pretend 8 players already occupy room 0.
    for pid in range(1, C.MAX_PLAYERS + 1):
        server.room_by_player_id[pid] = 0

    ws = FakeWebSocket([_spectator_hello(0)])
    result = asyncio.run(server._handshake(ws))

    assert result is not None  # not rejected with room_full
    welcome = json.loads(ws.sent[-1])
    assert welcome["type"] == "welcome"


def test_player_after_full_room_still_rejected():
    """Saturating room 0 with players still rejects a fresh
    *player* HELLO (regression: spectator cap exclusion must not
    leak to player path)."""
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    for pid in range(1, C.MAX_PLAYERS + 1):
        server.room_by_player_id[pid] = 0

    ws = FakeWebSocket([_hello(name="ninth", room_id=0)])
    result = asyncio.run(server._handshake(ws))

    assert result is None
    reject = json.loads(ws.sent[-1])
    assert reject["type"] == "reject"
    assert reject["data"]["reason"] == "room_full"


def test_player_pids_in_room_excludes_spectators():
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    server.room_by_player_id = {1: 0, 2: 0, 3: 0}
    server.spectator_pids = {2}
    assert sorted(server._player_pids_in_room(0)) == [1, 3]


def test_pids_in_room_still_returns_spectators():
    """Snapshot routing must include spectators so they receive
    broadcasts."""
    server = Server("127.0.0.1", 0, allowed_tokens={VALID_TOKEN}, rooms=1)
    server.room_by_player_id = {1: 0, 2: 0}
    server.spectator_pids = {2}
    assert sorted(server._pids_in_room(0)) == [1, 2]
