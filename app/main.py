import gc
import time

from machine import reset

try:
    from machine import WDT
except ImportError:
    WDT = False

from lib.button_detector import ButtonDetector
from lib.config_loader import load as load_config
from lib.device_identity import get_device_id
from lib.http_client import post_status
from lib.pins import AMP_IN_PIN, BUILTIN_BUTTON_PIN, DETECT_ADC_PIN, STATUS_RGB_PIN
from lib.reaction_sound import play_reaction
from lib.status_led import StatusLed
from lib.wifi_manager import WifiManager


def now_ms():
    return time.ticks_ms()


def elapsed_ms(start):
    return time.ticks_diff(now_ms(), start)


def make_watchdog(timeout_ms):
    if not WDT:
        return False
    try:
        return WDT(timeout=timeout_ms)
    except Exception as exc:
        print("watchdog disabled", exc)
        return False


def feed(wdt):
    if wdt:
        wdt.feed()


def maybe_reset(failures, limit, led):
    if failures >= limit:
        print("reset after failures", failures)
        led.resetting()
        time.sleep_ms(300)
        reset()


def build_post_url(template, device_id):
    try:
        return template.format(device_id=device_id)
    except Exception as exc:
        raise RuntimeError("bad post_url_template: {}".format(exc))


def post_with_retries(url, expected_status, timeout_sec, retries, retry_delay_ms):
    attempts = 1 + retries
    for attempt in range(1, attempts + 1):
        try:
            status = post_status(url, timeout_sec)
            print("POST", status)
            return status == expected_status
        except Exception as exc:
            print("POST error", attempt, exc)
            gc.collect()
            if attempt < attempts:
                time.sleep_ms(retry_delay_ms)
    return False


def wait_for_wifi(wifi, led, wdt, reset_after_failures):
    failures = 0
    while True:
        led.wifi_connecting()
        if wifi.ensure_connected():
            break
        failures += 1
        led.wifi_error()
        maybe_reset(failures, reset_after_failures, led)
        time.sleep_ms(1000)
        gc.collect()

    feed(wdt)


def main():
    config = load_config()
    device_id = get_device_id()
    post_url = build_post_url(config["post_url_template"], device_id)
    print("device_id", device_id)

    led = StatusLed(STATUS_RGB_PIN)
    led.starting()

    wdt = make_watchdog(config["watchdog_timeout_ms"])
    wifi = WifiManager(
        config["wifi_ssid"],
        config["wifi_password"],
        config["wifi_timeout_ms"],
    )
    wait_for_wifi(wifi, led, wdt, config["reset_after_failures"])

    button = ButtonDetector(
        DETECT_ADC_PIN,
        BUILTIN_BUTTON_PIN,
        config["adc_threshold"],
        config["cooldown_ms"],
    )

    failures = 0
    last_wifi_check = now_ms()
    last_gc = now_ms()

    led.ready()
    print("ready")

    while True:
        has_event, source, raw, builtin_value = button.read_event()
        if has_event:
            print("press", source, "raw", raw, "builtin", builtin_value)

            if not wifi.is_connected():
                led.wifi_connecting()
            if wifi.ensure_connected():
                feed(wdt)
                led.posting()
                ok = post_with_retries(
                    post_url,
                    config["expected_status"],
                    config["http_timeout_sec"],
                    config["post_retries"],
                    config["retry_delay_ms"],
                )
                if ok:
                    failures = 0
                    led.success()
                    feed(wdt)
                    play_reaction(AMP_IN_PIN)
                    led.ready()
                else:
                    failures += 1
                    led.post_error()
                    maybe_reset(failures, config["reset_after_failures"], led)
            else:
                failures += 1
                led.wifi_error()
                maybe_reset(failures, config["reset_after_failures"], led)

        if elapsed_ms(last_wifi_check) >= config["wifi_recheck_ms"]:
            last_wifi_check = now_ms()
            if wifi.is_connected():
                feed(wdt)
            else:
                failures += 1
                led.wifi_error()
                maybe_reset(failures, config["reset_after_failures"], led)

        if elapsed_ms(last_gc) >= config["gc_interval_ms"]:
            last_gc = now_ms()
            gc.collect()

        time.sleep_ms(5)


main()
