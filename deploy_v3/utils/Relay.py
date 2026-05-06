"""
Relay.py — I2C Relay Board Control (4-Channel)
ExpeDRY FeatherV2

Hardware: I2C relay module on SMBus bus=1, address=0x10
Channels: 1=ext humidifier, 2=int humidifier, 3=fan, 4=heater

Usage (module-level functions — no instance needed):
    from utils import Relay
    Relay.write(1, True)   # turn on channel 1
    state = Relay.read(1)  # read channel 1 state
"""

import time

try:
    from smbus2 import SMBus
    _BUS = 1
    _ADDR = 0x10
    _HAS_SMBUS = True
    # Verify relay is present at expected address
    try:
        with SMBus(_BUS) as _bus:
            _bus.read_byte(_ADDR)
        print(f'[RELAY] Found at I2C bus={_BUS} addr=0x{_ADDR:02x}')
    except Exception:
        # Scan common relay addresses
        _found = False
        for _try_addr in [0x10, 0x11, 0x20, 0x27]:
            try:
                with SMBus(_BUS) as _bus:
                    _bus.read_byte(_try_addr)
                _ADDR = _try_addr
                _found = True
                print(f'[RELAY] Found at I2C bus={_BUS} addr=0x{_ADDR:02x}')
                break
            except Exception:
                continue
        if not _found:
            print(f'[RELAY] No relay board detected on I2C bus {_BUS}')
except ImportError:
    _HAS_SMBUS = False
    print("smbus2 not installed — Relay module running in MOCK mode")

# Channel state cache (1-indexed, channels 1–4)
_state = {1: False, 2: False, 3: False, 4: False}


def write(channel: int, on: bool):
    """Set a relay channel on or off.

    Args:
        channel: 1–4 (1=ext hum, 2=int hum, 3=fan, 4=heater)
        on: True = closed/ON, False = open/OFF
    """
    if channel < 1 or channel > 4:
        print(f"Relay: invalid channel {channel}")
        return

    _state[channel] = bool(on)
    value = 0xFF if on else 0x00

    if _HAS_SMBUS:
        try:
            with SMBus(_BUS) as bus:
                bus.write_byte_data(_ADDR, channel, value)
        except Exception as e:
            print(f"Relay write error ch{channel}: {e}")
    else:
        print(f"Relay MOCK: ch{channel} = {'ON' if on else 'OFF'}")


def read(channel: int) -> bool:
    """Read the current state of a relay channel.

    Args:
        channel: 1–4

    Returns:
        True if ON, False if OFF
    """
    if channel < 1 or channel > 4:
        print(f"Relay: invalid channel {channel}")
        return False

    if _HAS_SMBUS:
        try:
            with SMBus(_BUS) as bus:
                val = bus.read_byte_data(_ADDR, channel)
                _state[channel] = val != 0x00
        except Exception as e:
            print(f"Relay read error ch{channel}: {e}")
    return _state[channel]


def all_off():
    """Turn all relay channels off."""
    for ch in range(1, 5):
        write(ch, False)
        time.sleep(0.1)
