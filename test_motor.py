import time
from adafruit_servokit import ServoKit

# Inicializamos el driver indicando que tiene 16 canales
print("Iniciando conexión con PCA9685...")
kit = ServoKit(channels=16)

# Configuramos los rangos de pulso para los servos SG90 (min, max)
# Esto es equivalente al SERVOMIN y SERVOMAX que usábamos en Arduino
for i in range(16):
    kit.servo[i].set_pulse_width_range(600, 2400)

pin_prueba = 9

try:
    print(f"Moviendo servo en el PIN {pin_prueba} a 90 grados (Centro)...")
    kit.servo[pin_prueba].angle = 90
    time.sleep(2)
    
    print("Moviendo a 45 grados...")
    kit.servo[pin_prueba].angle = 45
    time.sleep(1)
    
    print("Moviendo a 135 grados...")
    kit.servo[pin_prueba].angle = 135
    time.sleep(1)
    
    print("Regresando al centro y terminando.")
    kit.servo[pin_prueba].angle = 90

except KeyboardInterrupt:
    print("\nPrueba cancelada por el usuario.")
