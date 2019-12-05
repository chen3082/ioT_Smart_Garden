import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
print ("LED off")
while(1):
    GPIO.output(18,GPIO.LOW)
    time.sleep(1)
    #GPIO.output(18,GPIO.LOW)
    time.sleep(5)
    print('low')
    GPIO.output(18,GPIO.LOW)
    time.sleep(5)
    print('high')
    