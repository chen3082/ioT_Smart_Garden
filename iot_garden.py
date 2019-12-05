import time
import datetime
from firebase import firebase
import Adafruit_DHT
from board import SCL, SDA
import busio
import board
import adafruit_tsl2591
from adafruit_seesaw.seesaw import Seesaw
import RPi.GPIO as GPIO

watered = False

#SENSOR INTIALIZATION
#intit i2c
i2c_bus = busio.I2C(SCL, SDA)
#init humidity sensor dht22
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
#init soil sensor
ss = Seesaw(i2c_bus, addr=0x36) 
#init light sensor
lightsensor = adafruit_tsl2591.TSL2591(i2c_bus) 

#FIREBASE CONNECTION
firebase = firebase.FirebaseApplication('https://iot-garden-87415.firebaseio.com/', None)
print(firebase)
initTime = time.time()

#PLANTS WELL-BEING CONSTANT
TEMP_LOW = 12
TEMP_HIGH = 23
MOIST_LOW = 30
MOIST_HIGH = 60
LIGHT_TIME_LOW = 4
LIGHT_TIME_HIGH = 8
LUX_HIGH = 20000
LUX_LOW = 400


temp_list = []
moist_list = []
lux_list = []
light_time = 0
night_time = 0
while True:
    
    print ("received data in ", int(time.time() - initTime), "seconds")
    initTime = time.time()
    moisture = ss.moisture_read()  # read moisture level through capacitive touch pad
    temp = ss.get_temp()  # read temperature from the temperature sensor
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    lux = lightsensor.lux
    
    moisture = (100 * moisture / 1023)

    print ("temp = ", temp)
    print ("humidity = ", humidity)
    print ("light = ", lux)
    print ("moisture = ", moisture)
    
    temp_list.append(temp)
    moist_list.append(moisture)
    lux_list.append(lux)
    
    if (len(temp_list) > 30):
        temp_list.pop(0)
    if (len(moist_list) > 30):
        moist_list.pop(0)
    if (len(lux_list) > 30):
        lux_list.pop(0)
    
    for lux in lux_list:
        if (lux > LUX_LOW and lux < LUX_HIGH):
            light_time += 1
        else:
            night_time += 1
        
        if night_time > 6:
            light_time = 0
            night_time = 0
    print("Light time: ", light_time)
    print("Night time: ", night_time)    
    
    avg_temp = sum(temp_list) / len(temp_list)
    avg_moisture = sum(moist_list) / len(moist_list)
    
    firebase.put('iot-garden-87415','temperature',str(temp))
    firebase.put('iot-garden-87415', 'humidity', str(humidity))
    firebase.put('iot-garden-87415', 'light', str(lux))
    firebase.put('iot-garden-87415', 'moisture', str(moisture))
    
    
    
    mes = "\""
    if (avg_temp < TEMP_LOW):
        mes += "Plant is too COLD\n"
    elif (avg_temp > TEMP_HIGH):
        mes += "Plant is too HOT\n"
    
    if (avg_moisture < MOIST_LOW):
        mes += "Plant is DRY\n"
    elif (avg_moisture > MOIST_HIGH):
        mes += "Plant is WET\n"

        
    if (light_time < LIGHT_TIME_LOW):
        mes += "Plant need light\n"
    elif (light_time > LIGHT_TIME_HIGH):
        mes += "Plant has too much light\n"
    
    if mes == "\"":
        mes = "\"Plant is healthy\""
    else:
        mes += "\""

    print(mes)
    firebase.put('iot-garden-87415', 'mes', mes)
    # on or off pump and led
    firebase.put('iot-garden-87415', 'exposure', str(light_time))
    firebase.put('iot-garden-87415', 'avgtemp', str(avg_temp))
    pump = firebase.get('iot-garden-87415', 'motor_state')#return 0,1,2
    led = firebase.get('iot-garden-87415', 'light_state')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18,GPIO.OUT)
    GPIO.setup(23,GPIO.OUT)
    print("pump",pump)
    print("led",led)
    if pump == "0":
        GPIO.output(18,GPIO.LOW)
    elif pump == "1":
        GPIO.output(18,GPIO.HIGH)
    if led == "0":
        GPIO.output(23,GPIO.LOW)
    elif led == "1":
        GPIO.output(23,GPIO.HIGH)                                                            
        
#     if (update == unicode("1")):
#         print ("updating db")
#         firebase.put('iot-garden-monitoring-system', 'temperature', str(temp))
#         firebase.put('iot-garden-monitoring-system', 'humidity', str(humidity))
#         firebase.put('iot-garden-monitoring-system', 'light', str(light))
#         firebase.put('iot-garden-monitoring-system', 'moisture', str(moisture))
#         firebase.put('iot-garden-monitoring-system', 'update', str(0))
#         
#     if (motor_state == unicode("1")):
#         #turn on motor
#         print ("motor turned on")
#         grovepi.digitalWrite(motor,1)
#     elif (motor_state == unicode("2")):
#         #automate
#         print ("motor automatic control")
#         automate()
#     else:
#         #turn off motor
#         print ("motor turned off")
#         grovepi.digitalWrite(motor,0)
