"""PlayerCommand serialization for the INPUT message payload."""

from __future__ import annotations

from core.commands import PlayerCommand


def command_to_dict(cmd: PlayerCommand) -> dict[str, bool]:
    return {
        "rotate_left": cmd.rotate_left,
        "rotate_right": cmd.rotate_right,
        "thrust": cmd.thrust,
        "shoot": cmd.shoot,
        "hyperspace": cmd.hyperspace,
        "shield": cmd.shield,
    }


def dict_to_command(d: dict[str, bool]) -> PlayerCommand:
    return PlayerCommand(
        rotate_left=bool(d.get("rotate_left", False)),
        rotate_right=bool(d.get("rotate_right", False)),
        thrust=bool(d.get("thrust", False)),
        shoot=bool(d.get("shoot", False)),
        hyperspace=bool(d.get("hyperspace", False)),
        shield=bool(d.get("shield", False)),
    )
