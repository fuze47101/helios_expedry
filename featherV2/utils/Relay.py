# from smbus3 import SMBus

# DEVICE_BUS = 1
# DEVICE_ADDR = 0x10

# bus = SMBus(DEVICE_BUS)

# def write(pin, state):
#     command = 0xFF if state else 0x00
#     bus.write_byte_data(DEVICE_ADDR, pin, command)

# def read(pin):
#     state = bus.read_byte_data(DEVICE_ADDR, pin)
#     return state