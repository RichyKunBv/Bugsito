import time
from adafruit_servokit import ServoKit

print("--- CARGANDO TOPOLOGÍA DEL HEXÁPODO ---")
kit = ServoKit(channels=16)

# Tu mapa de puertos exacto
horizontales = [0, 2, 4, 6, 8, 10] # Izquierda/Derecha
verticales = [1, 3, 5, 7, 9, 11]   # Arriba/Abajo

def mover_grupo(pines, angulo, nombre_grupo):
    print(f"Moviendo {nombre_grupo} a {angulo}°...")
    for pin in pines:
        kit.servo[pin].angle = angulo
    time.sleep(1.5)

try:
    # 1. Posición de firmes (Todo al centro)
    print("\n1. Calibración: Todo al centro (90°)")
    mover_grupo(horizontales, 90, "Eje Horizontal")
    mover_grupo(verticales, 90, "Eje Vertical")
    
    # 2. Prueba de Caderas (Remo)
    print("\n2. Prueba de Caderas (Remo Izquierda/Derecha)")
    mover_grupo(horizontales, 45, "Eje Horizontal")
    mover_grupo(horizontales, 135, "Eje Horizontal")
    mover_grupo(horizontales, 90, "Eje Horizontal") # Regresa al centro
    
    # 3. Prueba de Rodillas (Lagartijas / Push-ups)
    print("\n3. Prueba de Rodillas (Lagartijas Arriba/Abajo)")
    mover_grupo(verticales, 45, "Eje Vertical")
    mover_grupo(verticales, 135, "Eje Vertical")
    mover_grupo(verticales, 90, "Eje Vertical") # Regresa al centro
    
    print("\n--- RUTINA COMPLETADA ---")

except KeyboardInterrupt:
    print("\nAbortando. Relajando motores...")
    # Apaga la señal PWM para que las patas queden "sueltas"
    for pin in range(12):
        kit.servo[pin].angle = None
