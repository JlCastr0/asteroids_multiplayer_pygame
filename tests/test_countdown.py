"""Tests for the Countdown timer in core.utils."""

from core.utils import Countdown


def test_default_is_inactive():
    c = Countdown()
    assert not c.active
    assert c.remaining == 0.0


def test_constructor_with_seconds_starts_active():
    c = Countdown(2.0)
    assert c.active
    assert c.remaining == 2.0


def test_tick_decrements_remaining():
    c = Countdown(1.0)
    fired = c.tick(0.25)
    assert not fired
    assert c.remaining == 0.75
    assert c.active


def test_tick_fires_true_once_when_reaching_zero():
    c = Countdown(0.5)
    c.tick(0.3)
    fired = c.tick(0.3)  # crosses zero
    assert fired is True
    assert not c.active


def test_tick_after_zero_returns_false():
    c = Countdown(0.5)
    c.tick(1.0)  # immediately exhausts
    fired = c.tick(0.1)
    assert fired is False


def test_reset_restarts_countdown():
    c = Countdown(0.1)
    c.tick(1.0)
    assert not c.active
    c.reset(2.0)
    assert c.active
    assert c.remaining == 2.0


def test_tick_on_inactive_does_nothing():
    c = Countdown()
    fired = c.tick(0.5)
    assert fired is False
    assert c.remaining == 0.0


def test_repeated_tick_to_zero_does_not_refire():
    c = Countdown(0.5)
    fired_first = c.tick(0.5)
    fired_second = c.tick(0.1)
    assert fired_first is True
    assert fired_second is False
