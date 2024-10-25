import RPi.GPIO as GPIO
from time import sleep


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 23 as output
buzzer=23
GPIO.setup(buzzer,GPIO.OUT)


GPIO.output(buzzer,GPIO.HIGH)
print ("Beep")
sleep(2) # Delay in seconds
GPIO.output(buzzer,GPIO.LOW)
print ("No Beep")
sleep(0.5)
    
