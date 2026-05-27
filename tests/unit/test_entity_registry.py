"""Unit tests for entity_registry read helpers."""

from tests.unit.helio_import import load_const, load_entity_registry

const = load_const()
entity_registry = load_entity_registry()

MODE_REST_ONLY = const.MODE_REST_ONLY
entities_for_mode = entity_registry.entities_for_mode
iter_action_specs = entity_registry.iter_action_specs
read_binary_value = entity_registry.read_binary_value
read_snapshot_key = entity_registry.read_snapshot_key
capability_enabled = entity_registry.capability_enabled


def test_read_snapshot_key_prefers_snapshot():
    data = {
        "snapshot": {"house_net_power_w": 42},
        "measurements": {"house": {"grid_net_w": 99}},
    }
    assert read_snapshot_key(data, "house_net_power_w") == 42


def test_read_second_channel_from_nested_measurements():
    data = {
        "snapshot": {},
        "measurements": {
            "second": {
                "active_import_w": 879,
                "active_export_w": 0,
                "energy_total_import_wh": 42599,
                "energy_day_import_wh": 407,
            },
            "raw_meter": {
                "voltage_second_v": 235.2,
                "current_second_a": 6.33,
                "pf_second": 0.59,
            },
        },
    }
    assert read_snapshot_key(data, "second_active_import_w") == 879
    assert read_snapshot_key(data, "second_voltage_v") == 235.2
    assert read_snapshot_key(data, "second_current_a") == 6.33
    assert read_snapshot_key(data, "second_energy_import_wh") == 42599
    assert read_snapshot_key(data, "second_day_energy_import_wh") == 407


def test_read_second_channel_prefers_snapshot():
    data = {
        "snapshot": {"second_active_import_w": 100},
        "measurements": {"second": {"active_import_w": 879}},
    }
    assert read_snapshot_key(data, "second_active_import_w") == 100


def test_triac_capability_from_raw_meter_voltage():
    data = {"measurements": {"raw_meter": {"voltage_second_v": 230.0}}, "snapshot": {}}
    assert capability_enabled(data, "triac_channel") is True


def test_read_binary_vacation_from_config():
    data = {"config": {"vacation_enabled": True}, "snapshot": {}}
    assert read_binary_value(data, "vacation") is True


def test_read_binary_on_off_from_snapshot():
    data = {"snapshot": {"source_stale": "ON"}}
    assert read_binary_value(data, "source_stale") is True


def test_linky_capability_gated():
    data = {"measurements": {}, "snapshot": {}}
    keys = {s.key for s in entities_for_mode(data, MODE_REST_ONLY)}
    assert "linky_ltarf" not in keys
    data_linky = {"measurements": {"linky_tariff": "HC"}, "snapshot": {}}
    keys2 = {s.key for s in entities_for_mode(data_linky, MODE_REST_ONLY)}
    assert "linky_ltarf" in keys2


def test_iter_action_specs_skips_index_zero():
    data = {
        "actions_config": {
            "actions": [
                {"title": "Triac"},
                {"title": "Heater 1"},
                {"title": "Heater 2"},
            ]
        }
    }
    specs = iter_action_specs(data)
    assert len(specs) == 2
    assert specs[0].key == "action_1"
    assert specs[0].action_index == 1
