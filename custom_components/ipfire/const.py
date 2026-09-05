from __future__ import annotations

DOMAIN = "ipfire"

CONF_URL = "url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VERIFY_SSL = "verify_ssl"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_URL = "https://ipfire.local:444"
DEFAULT_SCAN_INTERVAL = 30

MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 60

API_PATH = "/cgi-bin/api.cgi"
