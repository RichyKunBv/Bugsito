#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexápodo con marcha en trípode controlado por WASD
Configuración personalizable para tu disposición de patas
"""

import time
import curses
from adafruit_servokit import ServoKit

# ==================== CONFIGURACIÓN DEL ROBOT ====================
# Inicializar PCA9685
kit = ServoKit(channels=16, address=0x40)
for ch in range(16):
    kit.servo[ch].set_pulse_width_range(500, 2500)

# Mapeo de patas: (id, canal_h, canal_v, lado)
# lado: -1 = izquierda, 1 = derecha
# LLENA ESTOS DATOS SEGÚN TUS PRUEBAS
PATAS = {
    1: (0, 1, -1),   # ejemplo: pata 1 izquierda
    2: (2, 3, 1),    # pata 2 derecha
    3: (4, 5, -1),
    4: (6, 7, 1),
    5: (8, 9, -1),
    6: (10, 11, 1),
}

# Grupos de trípode (ajústalos según estabilidad)
GRUPO_A = [1, 4, 5]   # patas que se levantan juntas
GRUPO_B = [2, 3, 6]   # el otro grupo

# Ángulos de referencia (CALIBRA ESTOS CON TU ROBOT)
ANG_CADERA_CENTRO = 90          # cadera mirando hacia adelante
ANG_RODILLA_SOPORTE = 85        # rodilla en soporte (pata casi vertical)
ANG_RODILLA_AIRE = 135          # rodilla levantada (pata doblada)
RANGO_CADERA = 25               # desplazamiento máximo de cadera (grados)

# Parámetros de marcha
CICLO = 1.2                     # segundos por ciclo completo
T_LEVANTAR = 0.2
T_AVANZAR = 0.3
T_BAJAR = 0.2
# El resto es soporte

class Leg:
    def __init__(self, id_, ch_h, ch_v, lado):
        self.id = id_
        self.ch_h = ch_h
        self.ch_v = ch_v
        self.lado = lado          # -1 izquierda, 1 derecha
        self.ang_h = ANG_CADERA_CENTRO
        self.ang_v = ANG_RODILLA_SOPORTE
        self._update()
    
    def _update(self):
        kit.servo[self.ch_h].angle = self.ang_h
        kit.servo[self.ch_v].angle = self.ang_v
    
    def set_angles(self, h, v):
        self.ang_h = max(0, min(180, h))
        self.ang_v = max(0, min(180, v))
        self._update()

class Robot:
    def __init__(self):
        self.legs = {}
        for id_, (ch_h, ch_v, lado) in PATAS.items():
            self.legs[id_] = Leg(id_, ch_h, ch_v, lado)
        
        self.grupo_a = GRUPO_A
        self.grupo_b = GRUPO_B
        self.active_group = 'A'   # grupo que se mueve en el aire
        self.start_time = time.time()
        
        self.linear = 0.0
        self.angular = 0.0
        
        # Posición neutra inicial
        for leg in self.legs.values():
            leg.set_angles(ANG_CADERA_CENTRO, ANG_RODILLA_SOPORTE)
        time.sleep(1)
        print("Robot listo. Controles: W/A/S/D, Q parar, X salir")
    
    def set_speed(self, linear, angular):
        self.linear = max(-1.0, min(1.0, linear))
        self.angular = max(-1.0, min(1.0, angular))
    
    def update(self):
        now = time.time()
        elapsed = (now - self.start_time) % CICLO
        t = elapsed / CICLO
        
        # Determinar fase
        if t < T_LEVANTAR / CICLO:
            phase = 0
            frac = t / (T_LEVANTAR / CICLO)
        elif t < (T_LEVANTAR + T_AVANZAR) / CICLO:
            phase = 1
            frac = (t - T_LEVANTAR/CICLO) / (T_AVANZAR / CICLO)
        elif t < (T_LEVANTAR + T_AVANZAR + T_BAJAR) / CICLO:
            phase = 2
            frac = (t - (T_LEVANTAR+T_AVANZAR)/CICLO) / (T_BAJAR / CICLO)
        else:
            phase = 3
            frac = (t - (T_LEVANTAR+T_AVANZAR+T_BAJAR)/CICLO) / ((CICLO - T_LEVANTAR - T_AVANZAR - T_BAJAR)/CICLO)
        
        # Alternar grupo activo al inicio del ciclo
        if t < 0.01:
            self.active_group = 'B' if self.active_group == 'A' else 'A'
        
        # Calcular para cada pata
        for leg in self.legs.values():
            # ¿Está en el grupo activo?
            in_active = (self.active_group == 'A' and leg.id in self.grupo_a) or \
                        (self.active_group == 'B' and leg.id in self.grupo_b)
            
            # Ángulo centro de cadera (se desplaza con el giro)
            ang_center = ANG_CADERA_CENTRO + self.angular * 15 * leg.lado
            
            # Rango de movimiento según velocidad lineal
            range_h = self.linear * RANGO_CADERA
            if self.linear < 0:
                range_h = -range_h
            
            forward = ang_center + range_h
            backward = ang_center - range_h
            if forward < backward:
                forward, backward = backward, forward
            
            if in_active:
                # Pata en movimiento
                if phase == 0:   # levantando
                    v = ANG_RODILLA_SOPORTE + (ANG_RODILLA_AIRE - ANG_RODILLA_SOPORTE) * frac
                    h = backward
                elif phase == 1: # avanzando
                    v = ANG_RODILLA_AIRE
                    h = backward + (forward - backward) * frac
                elif phase == 2: # bajando
                    v = ANG_RODILLA_AIRE + (ANG_RODILLA_SOPORTE - ANG_RODILLA_AIRE) * frac
                    h = forward
                else:            # soporte (no debería pasar)
                    v = ANG_RODILLA_SOPORTE
                    h = forward
            else:
                # Pata en soporte
                v = ANG_RODILLA_SOPORTE
                # Cadera se mueve suavemente durante todo el ciclo
                h = forward + (backward - forward) * t
            
            leg.set_angles(h, v)

# ==================== CONTROL TECLADO ====================
def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.clear()
    
    robot = Robot()
    linear = 0.0
    angular = 0.0
    
    while True:
        key = stdscr.getch()
        if key != -1:
            if key == ord('w'):
                linear = 0.6
                angular = 0.0
            elif key == ord('s'):
                linear = -0.6
                angular = 0.0
            elif key == ord('a'):
                linear = 0.0
                angular = 0.5
            elif key == ord('d'):
                linear = 0.0
                angular = -0.5
            elif key == ord('q'):
                linear = 0.0
                angular = 0.0
            elif key == ord('x'):
                break
        
        robot.set_speed(linear, angular)
        robot.update()
        
        stdscr.addstr(0, 0, f"Vel: {linear:.2f}  Giro: {angular:.2f}   Grupo activo: {robot.active_group}")
        stdscr.addstr(1, 0, "W/A/S/D - Q parar - X salir")
        stdscr.refresh()
        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)
