import network
import time


def now_ms():
    return time.ticks_ms()


def elapsed_ms(start):
    return time.ticks_diff(now_ms(), start)


class WifiManager:
    def __init__(self, ssid, password, timeout_ms):
        self.ssid = ssid
        self.password = password
        self.timeout_ms = timeout_ms
        self.wlan = network.WLAN(network.STA_IF)

    def is_connected(self):
        return self.wlan.isconnected()

    def reset_radio(self):
        try:
            self.wlan.disconnect()
        except Exception:
            pass
        try:
            self.wlan.active(False)
        except Exception:
            pass
        time.sleep_ms(200)
        self.wlan.active(True)

    def ensure_connected(self):
        if self.wlan.isconnected():
            return True

        print("wifi reconnect")
        self.reset_radio()
        self.wlan.connect(self.ssid, self.password)

        start = now_ms()
        while elapsed_ms(start) < self.timeout_ms:
            if self.wlan.isconnected():
                print("wifi", self.wlan.ifconfig())
                return True
            time.sleep_ms(100)

        print("wifi failed")
        return False
