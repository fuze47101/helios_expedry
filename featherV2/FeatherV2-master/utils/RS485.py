import minimalmodbus

# PORT = '/dev/ttyUSB0'
PORT = 'COM5'
TEMP_REGISTER=0
HUM_REGISTER =1

class HumiditySenosr():
    instrument = minimalmodbus.Instrument

    def __init__(self) -> None:
        pass

    def connect(self, address):
        try:
            self.instrument=minimalmodbus.Instrument(PORT, address)
            self.instrument.serial.baudrate = 9600
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity   = minimalmodbus.serial.PARITY_NONE
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout  = 0.5
            self.instrument.mode = minimalmodbus.MODE_RTU
            self.instrument.clear_buffers_before_each_transaction = True 
            self.instrument.close_port_after_each_call = True
            #self.instrument.debug = True
            return True
        except Exception as e:
            print(e) #TODO:
            return False 

    def read(self):
        data = self.instrument.read_registers(0,2,3)
        temp = data[0]
        humd = data[1]
        return [temp/100, humd/100]
    
    def read_power(self):
        data = self.instrument.read_register(0,1,4)
        return data