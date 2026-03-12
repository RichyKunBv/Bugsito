import time
import board
import busio
from adafruit_pca9685 import PCA9685

print("Iniciando I2C en crudo...")
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)

# Obligamos a 50Hz, igual que el Arduino
pca.frequency = 50

# En Arduino el rango era 0-4095. Python usa 0-65535 (lo multiplicamos x 16)
# Arduino 150 (0 grados)  -> 150 * 16 = 2400
# Arduino 375 (90 grados) -> 375 * 16 = 6000
# Arduino 600 (180 grados)-> 600 * 16 = 9600

pin = 15

try:
    print(f"Mandando señal electrica RAW al PIN {pin}...")
    
    print("Forzando Centro (Pulso 375/6000)...")
    pca.channels[pin].duty_cycle = 6000
    time.sleep(2)
    
    print("Forzando 0 grados (Pulso 150/2400)...")
    pca.channels[pin].duty_cycle = 2400
    time.sleep(1)
    
    print("Forzando 180 grados (Pulso 600/9600)...")
    pca.channels[pin].duty_cycle = 9600
    time.sleep(1)
    
    print("Apagando señal PWM.")
    pca.channels[pin].duty_cycle = 0

except KeyboardInterrupt:
    pca.channels[pin].duty_cycle = 0
    print("\nCancelado.")
