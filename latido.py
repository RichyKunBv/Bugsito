import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
pin = 15

print("Enviando latido constante... presiona Ctrl+C para detener.")
try:
    while True:
        kit.servo[pin].angle = 45
        time.sleep(1)
        kit.servo[pin].angle = 135
        time.sleep(1)
except KeyboardInterrupt:
    print("Detenido.")
