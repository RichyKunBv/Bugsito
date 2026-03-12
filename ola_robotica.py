import time
from adafruit_servokit import ServoKit

print("--- INICIANDO PROTOCOLO DE PRUEBA MASIVA ---")
kit = ServoKit(channels=16)

# Vamos a probar del 0 al 14 (Ignoramos el 15 que está muerto)
pines_activos = range(0, 15)

try:
    print("1. Posición de descanso (90 grados)...")
    for pin in pines_activos:
        kit.servo[pin].angle = 90
    time.sleep(2)

    print("2. Movimiento sincronizado (Todos a 45 grados)...")
    for pin in pines_activos:
        kit.servo[pin].angle = 45
    time.sleep(1)

    print("3. Movimiento sincronizado (Todos a 135 grados)...")
    for pin in pines_activos:
        kit.servo[pin].angle = 135
    time.sleep(1)

    print("4. Iniciando 'La Ola' secuencial...")
    for pin in pines_activos:
        kit.servo[pin].angle = 45
        time.sleep(0.1)  # Retraso pequeñito entre cada motor
        
    for pin in pines_activos:
        kit.servo[pin].angle = 135
        time.sleep(0.1)

    print("5. Regresando a posición central...")
    for pin in pines_activos:
        kit.servo[pin].angle = 90
        
    print("--- PRUEBA FINALIZADA CON ÉXITO ---")

except KeyboardInterrupt:
    print("\nSecuencia abortada por el usuario. Apagando PWM...")
    # Apagado de emergencia
    for pin in pines_activos:
        kit.servo[pin].angle = None
