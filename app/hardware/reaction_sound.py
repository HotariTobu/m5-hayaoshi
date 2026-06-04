from machine import Pin, PWM
import time

PATTERN = [
    (1380, 120, 560, 540),
    (1120, 260, 540, 430),
    (1120, 560, 430, 0),
]


def tone(pwm, freq, ms, start_duty, end_duty):
    pwm.freq(freq)
    steps = max(1, min(24, ms // 20))
    step_ms = max(1, ms // steps)

    for index in range(steps):
        if steps == 1:
            duty = start_duty
        else:
            duty = start_duty + (end_duty - start_duty) * index // (steps - 1)
        pwm.duty(max(0, min(1023, duty)))
        time.sleep_ms(step_ms)


def play_reaction(pin):
    pwm = PWM(Pin(pin))
    try:
        for freq, ms, start_duty, end_duty in PATTERN:
            tone(pwm, freq, ms, start_duty, end_duty)
        pwm.duty(0)
        time.sleep_ms(20)
    finally:
        pwm.duty(0)
        pwm.deinit()
