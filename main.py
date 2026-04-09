#!/usr/bin/env python3
import time
import curses
import math
from adafruit_servokit import ServoKit

# Inicializar
kit = ServoKit(channels=16, address=0x40)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)

# Configuración de patas (solo 5 operativas)
# Ajusta las inversiones según tu montaje
patas = [
    {'id': 0, 'cad': 0, 'rod': 1, 'inv_cad': False, 'inv_rod': False},
    {'id': 1, 'cad': 2, 'rod': 3, 'inv_cad': False, 'inv_rod': False},
    {'id': 2, 'cad': 4, 'rod': 5, 'inv_cad': False, 'inv_rod': False},
    {'id': 3, 'cad': 6, 'rod': 7, 'inv_cad': False, 'inv_rod': False},
    {'id': 4, 'cad': 10, 'rod': 11, 'inv_cad': False, 'inv_rod': False},
]

# Ángulos determinados experimentalmente (cámbialos según tu robot)
ANG_CADERA_CENTRO = 90
ANG_CADERA_OFFSET = 25  # máx desplazamiento
ANG_RODILLA_SOPORTE = 85
ANG_RODILLA_AIRE = 135

# Tiempos de la marcha (en segundos)
T_LEVANTAR = 0.4
T_AVANZAR = 0.6
T_BAJAR = 0.4
T_SOPORTE = 0.8  # pausa entre pasos

class Robot:
    def __init__(self):
        self.patas = patas
        self.orden_patas = [0, 1, 2, 3, 4]  # orden de movimiento
        self.pata_actual = 0
        self.vel_lineal = 0.0  # -1 a 1
        self.vel_angular = 0.0
        self.activo = False
        self.tiempo_ultimo_paso = time.time()
        self.fase = 0  # 0: levantando, 1: avanzando, 2: bajando, 3: espera
        self.t_inicio_fase = time.time()
        
        # Inicializar todas las patas en posición neutra
        for p in self.patas:
            self.mover_pata(p, ANG_CADERA_CENTRO, ANG_RODILLA_SOPORTE)
        time.sleep(1)
    
    def set_servo(self, channel, angle, reverse):
        if reverse:
            angle = 180 - angle
        angle = max(0, min(180, angle))
        kit.servo[channel].angle = angle
    
    def mover_pata(self, pata, cad, rod):
        self.set_servo(pata['cad'], cad, pata['inv_cad'])
        self.set_servo(pata['rod'], rod, pata['inv_rod'])
    
    def set_velocidad(self, lineal, angular):
        self.vel_lineal = max(-1, min(1, lineal))
        self.vel_angular = max(-1, min(1, angular))
        if lineal == 0 and angular == 0:
            self.activo = False
        else:
            self.activo = True
    
    def update(self):
        if not self.activo:
            return
        
        ahora = time.time()
        dt = ahora - self.tiempo_ultimo_paso
        
        # Determinar la pata activa
        pata = self.patas[self.orden_patas[self.pata_actual]]
        
        # Calcular el rango de cadera según velocidad
        rango = self.vel_lineal * ANG_CADERA_OFFSET
        # Ajuste por giro: las patas izquierdas y derechas se mueven diferente
        # Asumimos que las patas con id par son izquierdas? Depende de tu montaje.
        # Por simplicidad, aquí no implementamos giro fino.
        
        # Posiciones de cadera para adelante y atrás
        adelante = ANG_CADERA_CENTRO - rango  # si rango positivo, adelante es menor ángulo
        atras = ANG_CADERA_CENTRO + rango
        
        # Asegurar que adelante < atrás para avanzar
        if adelante > atras:
            adelante, atras = atras, adelante
        
        # Máquina de estados para la pata activa
        if self.fase == 0:  # Levantando
            frac = (ahora - self.t_inicio_fase) / T_LEVANTAR
            if frac >= 1:
                frac = 1
                self.fase = 1
                self.t_inicio_fase = ahora
            rodilla = ANG_RODILLA_SOPORTE + (ANG_RODILLA_AIRE - ANG_RODILLA_SOPORTE) * frac
            cadera = atras
            self.mover_pata(pata, cadera, rodilla)
        
        elif self.fase == 1:  # Avanzando en el aire
            frac = (ahora - self.t_inicio_fase) / T_AVANZAR
            if frac >= 1:
                frac = 1
                self.fase = 2
                self.t_inicio_fase = ahora
            rodilla = ANG_RODILLA_AIRE
            cadera = atras + (adelante - atras) * frac
            self.mover_pata(pata, cadera, rodilla)
        
        elif self.fase == 2:  # Bajando
            frac = (ahora - self.t_inicio_fase) / T_BAJAR
            if frac >= 1:
                frac = 1
                self.fase = 3
                self.t_inicio_fase = ahora
            rodilla = ANG_RODILLA_AIRE + (ANG_RODILLA_SOPORTE - ANG_RODILLA_AIRE) * frac
            cadera = adelante
            self.mover_pata(pata, cadera, rodilla)
        
        elif self.fase == 3:  # Espera (soporte)
            # Durante la espera, las patas inactivas están en soporte y la activa también
            # Pero aquí solo manejamos la activa. Las demás se actualizan en otro lugar.
            if ahora - self.t_inicio_fase >= T_SOPORTE:
                self.fase = 0
                self.pata_actual = (self.pata_actual + 1) % len(self.orden_patas)
                self.t_inicio_fase = ahora
        
        # Actualizar las demás patas (las que están en soporte)
        for i, p in enumerate(self.patas):
            if i != self.orden_patas[self.pata_actual]:
                # En soporte, la cadera se mueve lentamente de adelante a atrás
                # Calculamos el progreso del ciclo total
                ciclo_total = T_LEVANTAR + T_AVANZAR + T_BAJAR + T_SOPORTE
                tiempo_en_ciclo = (ahora - self.tiempo_ultimo_paso) % ciclo_total
                t_norm = tiempo_en_ciclo / ciclo_total
                # La cadera se mueve desde adelante hacia atrás durante todo el ciclo
                cadera_soporte = adelante + (atras - adelante) * t_norm
                self.mover_pata(p, cadera_soporte, ANG_RODILLA_SOPORTE)
        
        self.tiempo_ultimo_paso = ahora

def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.clear()
    
    robot = Robot()
    
    v = 0.0
    w = 0.0
    
    while True:
        key = stdscr.getch()
        if key != -1:
            if key == ord('w'):
                v = 0.5
                w = 0.0
            elif key == ord('s'):
                v = -0.5
                w = 0.0
            elif key == ord('a'):
                v = 0.0
                w = 0.3
            elif key == ord('d'):
                v = 0.0
                w = -0.3
            elif key == ord('q'):
                v = 0.0
                w = 0.0
            elif key == ord('x'):
                break
        
        robot.set_velocidad(v, w)
        robot.update()
        
        stdscr.addstr(0, 0, f"Vel lineal: {v:.2f}  Vel angular: {w:.2f}   ")
        stdscr.addstr(1, 0, f"Pata activa: {robot.orden_patas[robot.pata_actual]}  Fase: {robot.fase}")
        stdscr.addstr(2, 0, "Controles: W/A/S/D - Q parar - X salir")
        stdscr.refresh()
        
        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
