import time
from adafruit_servokit import ServoKit

class HexapodoPredator:
    def __init__(self):
        print("[💀] INICIANDO PROTOCOLO DEPREDADOR V2.0...")
        self.kit = ServoKit(channels=16)
        
        # Mapeo de puertos
        self.horizontales = [0, 2, 4, 6, 8, 10]
        self.verticales =   [1, 3, 5, 7, 9, 11]
        
        # Separación en Escuadrones para la Marcha en Trípode
        # Escuadrón A: Patas 1, 3, 5
        self.tripode_A_H = [self.horizontales[0], self.horizontales[2], self.horizontales[4]]
        self.tripode_A_V = [self.verticales[0], self.verticales[2], self.verticales[4]]
        
        # Escuadrón B: Patas 2, 4, 6
        self.tripode_B_H = [self.horizontales[1], self.horizontales[3], self.horizontales[5]]
        self.tripode_B_V = [self.verticales[1], self.verticales[3], self.verticales[5]]

    def mover_suave(self, pines, angulo_destino, pasos=15, velocidad=0.01):
        """Movimiento progresivo para no quemar las baterías por picos de amperaje"""
        # Obtenemos el ángulo actual del primer motor para calcular la ruta
        # (Si no tiene ángulo previo, asumimos 90)
        angulo_actual = self.kit.servo[pines[0]].angle or 90
        incremento = (angulo_destino - angulo_actual) / pasos
        
        for i in range(pasos):
            angulo_temp = angulo_actual + (incremento * i)
            for pin in pines:
                self.kit.servo[pin].angle = angulo_temp
            time.sleep(velocidad)
            
        # Forzar posición final exacta
        for pin in pines:
            self.kit.servo[pin].angle = angulo_destino

    def despertar(self):
        print("\n[+] 1. Encendiendo sistemas y levantando chasis...")
        # Alinea caderas
        self.mover_suave(self.horizontales, 90)
        # Sube el cuerpo empujando las rodillas
        self.mover_suave(self.verticales, 45, pasos=30, velocidad=0.02)
        time.sleep(1)

    def postura_amenaza(self):
        print("\n[!] 2. INICIANDO POSTURA DE AMENAZA")
        # Levanta solo las dos patas delanteras altísimo
        patas_delanteras_v = [self.verticales[0], self.verticales[1]]
        patas_delanteras_h = [self.horizontales[0], self.horizontales[1]]
        
        self.mover_suave(patas_delanteras_v, 140) # Patas arriba
        self.mover_suave(patas_delanteras_h, 45)  # Abre las "garras"
        time.sleep(1.5)
        
        # Regresa a la posición neutral
        self.mover_suave(patas_delanteras_h, 90)
        self.mover_suave(patas_delanteras_v, 45)
        time.sleep(0.5)

    def marcha_tripoide(self, pasos_a_dar=3):
        print(f"\n[>>] 3. EJECUTANDO MARCHA EN TRÍPODE ({pasos_a_dar} pasos)...")
        # Variables de ángulo para caminar (Ajusta si camina chueco)
        rodilla_arriba = 90  # Levanta la pata
        rodilla_suelo = 45   # Pata empujando el suelo
        cadera_adelante = 120 # Mueve la pierna hacia adelante
        cadera_atras = 60    # Empuja el cuerpo hacia adelante
        
        for paso in range(pasos_a_dar):
            print(f"   [-] Paso {paso + 1}...")
            # --- FASE 1: Mueve Trípode A ---
            # Levanta el Escuadrón A
            self.mover_suave(self.tripode_A_V, rodilla_arriba, velocidad=0.005)
            # Avanza caderas Escuadrón A en el aire, retrasa caderas Escuadrón B en el suelo (empuje)
            self.mover_suave(self.tripode_A_H, cadera_adelante, velocidad=0.005)
            self.mover_suave(self.tripode_B_H, cadera_atras, velocidad=0.005)
            # Baja el Escuadrón A al suelo
            self.mover_suave(self.tripode_A_V, rodilla_suelo, velocidad=0.005)
            
            # --- FASE 2: Mueve Trípode B ---
            # Levanta el Escuadrón B
            self.mover_suave(self.tripode_B_V, rodilla_arriba, velocidad=0.005)
            # Avanza caderas Escuadrón B en el aire, retrasa caderas Escuadrón A en el suelo (empuje)
            self.mover_suave(self.tripode_B_H, cadera_adelante, velocidad=0.005)
            self.mover_suave(self.tripode_A_H, cadera_atras, velocidad=0.005)
            # Baja el Escuadrón B al suelo
            self.mover_suave(self.tripode_B_V, rodilla_suelo, velocidad=0.005)

    def colapso_sistema(self):
        print("\n[+] 4. Apagando servidor físico. Colapsando...")
        self.mover_suave(self.horizontales, 90)
        # Baja el chasis lentamente hasta tocar el suelo
        self.mover_suave(self.verticales, 130, pasos=30, velocidad=0.03)
        
        # Apagado total del PWM para no gastar batería
        for i in range(12):
            self.kit.servo[i].angle = None
        print("[💀] Sistema offline.")

# ==================================
# BLOQUE PRINCIPAL
# ==================================
if __name__ == "__main__":
    robot = HexapodoPredator()
    try:
        robot.despertar()
        robot.postura_amenaza()
        
        # ¡OJO! Aquí el robot va a intentar avanzar. 
        robot.marcha_tripoide(pasos_a_dar=4)
        
        # Regresa todas las caderas al centro antes de dormir
        robot.mover_suave(robot.horizontales, 90)
        time.sleep(1)
        
        robot.colapso_sistema()
        
    except KeyboardInterrupt:
        print("\n[!] Aborto de emergencia por SysAdmin.")
        for pin in range(12):
            robot.kit.servo[pin].angle = None
