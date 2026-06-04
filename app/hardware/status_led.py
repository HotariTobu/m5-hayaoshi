from machine import Pin


class StatusLed:
    def __init__(self, pin):
        self.enabled = False
        try:
            from neopixel import NeoPixel
            self.pin = Pin(pin, Pin.OUT)
            self.pixel = NeoPixel(self.pin, 1)
            self.enabled = True
            self.off()
        except Exception as exc:
            print("status led disabled", exc)

    def color(self, value):
        if not self.enabled:
            return
        self.pixel[0] = value
        self.pixel.write()

    def off(self):
        self.color((0, 0, 0))

    def starting(self):
        self.color((20, 20, 20))

    def wifi_connecting(self):
        self.color((60, 45, 0))

    def ready(self):
        self.color((0, 0, 30))

    def posting(self):
        self.color((0, 35, 35))

    def success(self):
        self.color((0, 50, 0))

    def wifi_error(self):
        self.color((60, 0, 0))

    def post_error(self):
        self.color((45, 0, 45))

    def resetting(self):
        self.color((50, 50, 50))
