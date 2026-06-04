from machine import unique_id
import ubinascii


def get_device_id():
    return ubinascii.hexlify(unique_id()).decode()
