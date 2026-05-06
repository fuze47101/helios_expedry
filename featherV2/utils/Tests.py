x_point = 0
duration = 60
interval = 1

def moisture_movement(): #test 1
    if not self.started: #Start test
        self.hum2_status = True
        time.sleep(.2)
        self.fan_status = True 
    elif self.x_point == self.duration: #Begin Extraction
        self.started = True
        self.hum2_status = False
        time.sleep(.2)
        self.fan_status = True 
    elif not self.running: #Stop everything
        self.hum2_status = False
        time.sleep(.2)
        self.fan_status = False

def moisture_resitance(): #Test 2
    if self.x_point == self.duration:
        self.started = True
        self.hum1_status = False
        time.sleep(.2)
        self.fan_status = True
    elif not self.started:
        self.hum1_status = True
        time.sleep(.2)
        self.fan_status = False
    elif self.started and self.current_humd <= self.endpoint:
        self.hum1_status = False
        time.sleep(.2)
        self.fan_status = False
        self.running = False
        self.can_save = True if self.data_save else False
    elif not self.running:
        self.hum1_status = False
        time.sleep(.2)
        self.fan_status = False

def thermal():

    pass


def update_time():
    pass