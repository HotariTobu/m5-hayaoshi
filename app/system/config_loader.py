import os
import ujson

CONFIG_PATH = "config.json"

REQUIRED_STRING_FIELDS = (
    "wifi_ssid",
    "wifi_password",
    "post_url_template",
)

REQUIRED_INT_FIELDS = (
    "expected_status",
    "adc_threshold",
    "cooldown_ms",
    "wifi_timeout_ms",
    "wifi_recheck_ms",
    "http_timeout_sec",
    "post_retries",
    "retry_delay_ms",
    "reset_after_failures",
    "watchdog_timeout_ms",
    "gc_interval_ms",
)

ALLOWED_FIELDS = REQUIRED_STRING_FIELDS + REQUIRED_INT_FIELDS


def require_known_fields(config):
    for name in config:
        if name not in ALLOWED_FIELDS:
            raise RuntimeError("unknown config field: {}".format(name))


def require_present(config):
    for name in ALLOWED_FIELDS:
        if name not in config:
            raise RuntimeError("missing config field: {}".format(name))


def require_strings(config):
    for name in REQUIRED_STRING_FIELDS:
        value = config[name]
        if not isinstance(value, str) or not value:
            raise RuntimeError("{} must be a non-empty string".format(name))

    if "{device_id}" not in config["post_url_template"]:
        raise RuntimeError("post_url_template must include {device_id}")


def require_int_min(config, name, minimum):
    value = config[name]
    if not isinstance(value, int):
        raise RuntimeError("{} must be an integer".format(name))
    if value < minimum:
        raise RuntimeError("{} must be >= {}".format(name, minimum))


def require_int_range(config, name, minimum, maximum):
    require_int_min(config, name, minimum)
    value = config[name]
    if value > maximum:
        raise RuntimeError("{} must be <= {}".format(name, maximum))


def require_ints(config):
    require_int_range(config, "expected_status", 100, 599)
    require_int_range(config, "adc_threshold", 0, 4095)
    require_int_min(config, "cooldown_ms", 1)
    require_int_min(config, "wifi_timeout_ms", 1)
    require_int_min(config, "wifi_recheck_ms", 1)
    require_int_min(config, "http_timeout_sec", 1)
    require_int_min(config, "post_retries", 0)
    require_int_min(config, "retry_delay_ms", 0)
    require_int_min(config, "reset_after_failures", 1)
    require_int_min(config, "watchdog_timeout_ms", 1)
    require_int_min(config, "gc_interval_ms", 1)


def validate(config):
    require_known_fields(config)
    require_present(config)
    require_strings(config)
    require_ints(config)


def load(path=CONFIG_PATH):
    with open(path) as config_file:
        config = ujson.load(config_file)
    validate(config)
    return config


def save_atomic(config, path=CONFIG_PATH):
    validate(config)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as config_file:
        config_file.write(ujson.dumps(config))
    try:
        os.remove(path)
    except OSError:
        pass
    os.rename(tmp_path, path)
