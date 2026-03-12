import time
import math
import sys
from adafruit_servokit import ServoKit

class HexapodoSO:
    def __init__(self):
        print("[+] Iniciando Sistema Operativo del Hexápodo V1.0...")
        try:
            self.kit = ServoKit(channels=16)
        except Exception as e:
            print(f"[!] Error crítico en I2C: {e}")
            sys.exit(1)
            
        # Topología de la bestia
        self.horizontales = [0, 2, 4, 6, 8, 10] # Caderas
        self.verticales = [1, 3, 5, 7, 9, 11]   # Rodillas
        self.posicion_actual = {pin: 90 for pin in range(12)}
        
        print("[+] Hardware conectado y mapeado. Baterías listas.")

    def mover_suave(self, pines, angulo_destino, velocidad=0.02):
        """Mueve un grupo de motores poco a poco para no dar tirones eléctricos"""
        pasos = 20
        # Tomamos el ángulo actual del primer pin del grupo como referencia
        angulo_inicial = self.posicion_actual[pines[0]]
        incremento = (angulo_destino - angulo_inicial) / pasos
        
        for i in range(pasos):
            angulo_temp = angulo_inicial + (incremento * i)
            for pin in pines:
                self.kit.servo[pin].angle = angulo_temp
                self.posicion_actual[pin] = angulo_temp
            time.sleep(velocidad)
            
        # Asegurar posición final
        for pin in pines:
            self.kit.servo[pin].angle = angulo_destino
            self.posicion_actual[pin] = angulo_destino

    def despertar(self):
        print("\n[*] Secuencia: DESPERTAR")
        # Primero acomoda las caderas
        self.mover_suave(self.horizontales, 90, 0.01)
        # Luego se levanta lentamente
        self.mover_suave(self.verticales, 45, 0.03)
        time.sleep(0.5)

    def modo_combate(self):
        print("\n[*] Secuencia: MODO COMBATE (Postura baja)")
        # Abre las patas y baja el centro de gravedad
        self.mover_suave(self.horizontales, 120, 0.02)
        self.mover_suave(self.verticales, 110, 0.02)
        time.sleep(1)

    def respirar(self, ciclos=5):
        print("\n[*] Secuencia: RESPIRACIÓN ORGÁNICA (Idle animation)")
        # Usa trigonometría para simular que el robot respira subiendo y bajando
        amplitud = 15  # Qué tanto sube y baja
        centro = 90    # Punto medio de las rodillas
        
        for i in range(ciclos * 40): # 40 pasos por ciclo
            onda = math.sin(i * 0.15)
            angulo_respiracion = centro + (onda * amplitud)
            
            for pin in self.verticales:
                self.kit.servo[pin].angle = angulo_respiracion
                self.posicion_actual[pin] = angulo_respiracion
            time.sleep(0.02)

    def dormir(self):
        print("\n[*] Secuencia: APAGADO DE EMERGENCIA")
        # Baja el cuerpo al suelo suavemente
        self.mover_suave(self.verticales, 135, 0.04)
        print("[+] Relajando músculos (PWM OFF)...")
        for pin in range(12):
            self.kit.servo[pin].angle = None
        print("[+] Servidor Hexápodo apagado. Buenas noches.")

# ==========================================
# EJECUCIÓN DEL SCRIPT
# ==========================================
if __name__ == "__main__":
    arana = HexapodoSO()
    
    try:
        arana.despertar()
        time.sleep(1)
        
        arana.modo_combate()
        time.sleep(1)
        
        arana.respirar(ciclos=6) # Se queda "respirando" un rato
        
        arana.dormir()
        
    except KeyboardInterrupt:
        arana.dormir()
