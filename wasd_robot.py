import time
import sys
import tty
import termios
from adafruit_servokit import ServoKit

class HexapodoTarantula:
    def __init__(self):
        print("\n[+] INICIANDO SISTEMA DE CONTROL: MODO TARÁNTULA (5 PATAS)...")
        self.kit = ServoKit(channels=16)
        
        # Topología con pata 5 amputada (ignoramos 8 y 9)
        self.horizontales = [0, 2, 4, 6, 10] 
        self.verticales =   [1, 3, 5, 7, 11] 
        
        self.escuadron_A_H = [0, 4]
        self.escuadron_A_V = [1, 5]
        
        self.escuadron_B_H = [2, 6, 10]
        self.escuadron_B_V = [3, 7, 11]

        # --- PARÁMETROS DE ARAÑA REAL (EXAGERADOS) ---
        self.rodilla_suelo = 110  # Empuja el piso para levantar la panza
        self.rodilla_aire = 20    # Levanta la pata ALTÍSIMO
        self.cadera_centro = 90
        
        self.despertar()

    def mover_suave(self, pines, angulo_destino, pasos=10, retardo=0.005):
        """Movimiento fluido para zancadas largas sin tirones"""
        angulo_actual = self.kit.servo[pines[0]].angle or 90
        incremento = (angulo_destino - angulo_actual) / pasos
        
        for i in range(pasos):
            angulo_temp = angulo_actual + (incremento * i)
            for pin in pines:
                self.kit.servo[pin].angle = angulo_temp
            time.sleep(retardo)
            
        for pin in pines:
            self.kit.servo[pin].angle = angulo_destino

    def despertar(self):
        print("[+] Levantando chasis (Posición de Tarántula)...")
        self.mover_suave(self.horizontales, self.cadera_centro)
        # Se pone de "puntillas"
        self.mover_suave(self.verticales, self.rodilla_suelo, pasos=20, retardo=0.02)

    def paso_arana(self, direccion):
        """Secuencia de marcha con elevación extrema de patas"""
        # Zancadas súper largas
        if direccion == 'w': # Adelante
            impulso = 135
            arrastre = 45
        elif direccion == 's': # Atrás
            impulso = 45
            arrastre = 135
        elif direccion == 'a': # Rotar Izquierda
            impulso = 120
            arrastre = 120
        elif direccion == 'd': # Rotar Derecha
            impulso = 60
            arrastre = 60
        else:
            return

        # --- FASE 1: Mueve Escuadrón A ---
        # 1. Levanta las patas A hasta arriba (Modo araña)
        self.mover_suave(self.escuadron_A_V, self.rodilla_aire) 
        # 2. Las patas A se estiran hacia adelante en el aire | Las B (en el piso) empujan el cuerpo
        self.mover_suave(self.escuadron_A_H, impulso)
        self.mover_suave(self.escuadron_B_H, arrastre)
        # 3. Clava las patas A en el piso
        self.mover_suave(self.escuadron_A_V, self.rodilla_suelo) 

        # --- FASE 2: Mueve Escuadrón B ---
        # 1. Levanta las patas B hasta arriba
        self.mover_suave(self.escuadron_B_V, self.rodilla_aire) 
        # 2. Las patas B se estiran en el aire | Las A (en el piso) empujan el cuerpo
        self.mover_suave(self.escuadron_B_H, impulso)
        self.mover_suave(self.escuadron_A_H, arrastre)
        # 3. Clava las patas B en el piso
        self.mover_suave(self.escuadron_B_V, self.rodilla_suelo)

    def dormir(self):
        print("\n[+] Aterrizando nave...")
        self.mover_suave(self.horizontales, 90)
        self.mover_suave(self.verticales, 140, pasos=20, retardo=0.02)
        for pin in range(12):
            self.kit.servo[pin].angle = None
        print("[💀] Motores liberados.")

# ==========================================
# LECTOR DE TECLADO 
# ==========================================
def obtener_tecla():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == "__main__":
    robot = HexapodoTarantula()
    
    print("\n" + "="*45)
    print(" CONTROL DE TARÁNTULA (Presiona 'x' para salir)")
    print("          [ W ] -> Avanzar")
    print("   [ A ]  [ S ]  [ D ] -> Izq / Atrás / Der")
    print("="*45 + "\n")

    try:
        while True:
            tecla = obtener_tecla().lower()
            
            if tecla == 'x':
                break
            elif tecla in ['w', 'a', 's', 'd']:
                sys.stdout.write(f"\rEjecutando paso de tarántula: [{tecla.upper()}]  ")
                sys.stdout.flush()
                robot.paso_arana(tecla)
                
    except Exception as e:
        print(f"\n[!] Error detectado: {e}")
    finally:
        robot.dormir()
