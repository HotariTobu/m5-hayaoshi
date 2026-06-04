from machine import ADC, Pin
import time


def now_ms():
    return time.ticks_ms()


def elapsed_ms(start):
    return time.ticks_diff(now_ms(), start)


class BoardButtonSignal:
    def __init__(self, pin, threshold):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.threshold = threshold

    def read_pressed(self):
        raw = self.adc.read()
        return raw < self.threshold, raw


class BuiltinButtonSignal:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)

    def read_pressed(self):
        value = self.pin.value()
        return value == 0, value


class ButtonDetector:
    def __init__(self, adc_pin, builtin_pin, threshold, cooldown_ms):
        self.board = BoardButtonSignal(adc_pin, threshold)
        self.builtin = BuiltinButtonSignal(builtin_pin)
        self.cooldown_ms = cooldown_ms
        self.in_pressed = False
        self.last_event = now_ms() - cooldown_ms

    def read_event(self):
        board_pressed, raw = self.board.read_pressed()
        builtin_pressed, builtin_value = self.builtin.read_pressed()
        pressed = board_pressed or builtin_pressed
        has_event = False
        source = "none"

        if pressed and not self.in_pressed and elapsed_ms(self.last_event) >= self.cooldown_ms:
            self.last_event = now_ms()
            has_event = True
            if board_pressed and builtin_pressed:
                source = "both"
            elif board_pressed:
                source = "board"
            else:
                source = "pico"

        self.in_pressed = pressed
        return has_event, source, raw, builtin_value
