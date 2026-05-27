"""Constants for HelioZero integration."""

DOMAIN = "helio_zero"
CONF_HOST = "host"
CONF_API_TOKEN = "api_token"
CONF_INTEGRATION_MODE = "integration_mode"
CONF_SCAN_INTERVAL = "scan_interval"

MODE_COMPANION = "companion"
MODE_REST_ONLY = "rest_only"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 1
MAX_SCAN_INTERVAL = 300

COMPANION_ENTITY_KEYS = frozenset({"republish_discovery"})
