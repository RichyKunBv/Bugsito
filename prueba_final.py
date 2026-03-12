import time
from adafruit_servokit import ServoKit

print("--- INICIANDO PRUEBA CON TRADUCTOR LÓGICO ---")
print("Conectando con el PCA9685 a 5V...")

# Inicializamos el driver
kit = ServoKit(channels=16)

# Usamos tu pin de pruebas
pin_prueba = 11

try:
    print("¡Orden enviada! Moviendo a 90 grados (Centro)...")
    kit.servo[pin_prueba].angle = 90
    time.sleep(1.5)
    
    print("Moviendo a 45 grados...")
    kit.servo[pin_prueba].angle = 45
    time.sleep(1.5)
    
    print("Moviendo a 135 grados...")
    kit.servo[pin_prueba].angle = 135
    time.sleep(1.5)
    
    print("Regresando al centro (90 grados)...")
    kit.servo[pin_prueba].angle = 90
    print("¡PRUEBA FINALIZADA CON ÉXITO!")

except KeyboardInterrupt:
    print("\nPrueba cancelada.")
