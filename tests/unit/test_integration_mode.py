"""Unit tests for companion vs rest_only filtering."""

from tests.unit.helio_import import load_const, load_entity_registry, load_integration_mode

const = load_const()
integration_mode = load_integration_mode()
entity_registry = load_entity_registry()

MODE_COMPANION = const.MODE_COMPANION
MODE_REST_ONLY = const.MODE_REST_ONLY
entities_for_mode = entity_registry.entities_for_mode
entity_enabled_for_mode = integration_mode.entity_enabled_for_mode


def test_companion_only_republish():
    assert entity_enabled_for_mode("republish_discovery", MODE_COMPANION)
    assert not entity_enabled_for_mode("vacation", MODE_COMPANION)
    assert entity_enabled_for_mode("vacation", MODE_REST_ONLY)


def test_rest_only_includes_sensors():
    data = {"measurements": {"house": {"grid_net_w": 100}}, "snapshot": {}}
    keys = {s.key for s in entities_for_mode(data, MODE_REST_ONLY, platform="sensor")}
    assert "house_net_power_w" in keys
    assert "triac_open_percent" in keys


def test_companion_entity_list():
    data = {"measurements": {}, "snapshot": {}}
    keys = {s.key for s in entities_for_mode(data, MODE_COMPANION)}
    assert keys == {"republish_discovery"}
