#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexápodo con marcha en trípode - Control WASD
Optimizado para SG90 (ángulo de rodilla ~90° en soporte)
"""

import time
import curses
from adafruit_servokit import ServoKit

# ========== CONFIGURACIÓN DEL PCA9685 ==========
kit = ServoKit(channels=16, address=0x40)
for ch in range(16):
    kit.servo[ch].set_pulse_width_range(500, 2500)  # rango SG90

# ========== MAPEO DE PATAS (canal_cadera, canal_rodilla) ==========
PATAS = {
    1: (0, 1),
    2: (2, 3),
    3: (4, 5),
    4: (6, 7),
    5: (8, 9),
    6: (10, 11),
}

# ========== ÁNGULOS NEUTROS (CALIBRAR) ==========
# Completa estos valores según la posición real de tu robot.
# Para empezar, usa 90° en ambos, pero luego ajústalos.
CADERA_ADELANTE = {i: 90 for i in range(1, 7)}   # ángulo donde la pata apunta hacia adelante
RODILLA_VERTICAL = {i: 90 for i in range(1, 7)}  # ángulo donde la pata queda vertical (pie debajo del cuerpo)

# Ángulo para levantar la pata (más doblada)
RODILLA_AIRE = 130   # ajusta según tu mecánica

# Rango de movimiento de la cadera (grados desde la posición adelante)
RANGO_CADERA = 25    # reduce si los servos no tienen fuerza

# ========== PARÁMETROS DE LA MARCHA ==========
CICLO = 1.5          # segundos por ciclo completo (más lento = más torque)
T_LEVANTAR = 0.25
T_AVANZAR = 0.4
T_BAJAR = 0.25

# Grupos de trípode (dos grupos que se alternan)
# Ajusta estos grupos según la estabilidad de tu robot.
GRUPO_A = [1, 4, 5]   # patas que se levantan juntas
GRUPO_B = [2, 3, 6]   # el otro grupo

# ========== CLASE PATA ==========
class Leg:
    def __init__(self, id_, ch_h, ch_v):
        self.id = id_
        self.ch_h = ch_h
        self.ch_v = ch_v
        self.ang_h = CADERA_ADELANTE[id_]
        self.ang_v = RODILLA_VERTICAL[id_]
        self._update()

    def _update(self):
        kit.servo[self.ch_h].angle = self.ang_h
        kit.servo[self.ch_v].angle = self.ang_v

    def set_angles(self, h, v):
        self.ang_h = max(0, min(180, h))
        self.ang_v = max(0, min(180, v))
        self._update()

# ========== CLASE ROBOT ==========
class Robot:
    def __init__(self):
        self.legs = {}
        for id_, (ch_h, ch_v) in PATAS.items():
            self.legs[id_] = Leg(id_, ch_h, ch_v)

        self.grupo_a = GRUPO_A
        self.grupo_b = GRUPO_B
        self.active_group = 'A'    # grupo que se mueve (el otro apoya)
        self.start_time = time.time()

        self.linear = 0.0   # velocidad lineal (-1..1)
        self.angular = 0.0  # velocidad angular (-1..1)

        # Posición inicial neutra
        self.reset()

    def reset(self):
        """Vuelve a la posición neutra (todas las patas apoyadas)"""
        for leg in self.legs.values():
            leg.set_angles(CADERA_ADELANTE[leg.id], RODILLA_VERTICAL[leg.id])
        time.sleep(0.5)

    def set_speed(self, linear, angular):
        self.linear = max(-1.0, min(1.0, linear))
        self.angular = max(-1.0, min(1.0, angular))

    def update(self):
        """Actualiza la posición de todas las patas según el tiempo y la velocidad"""
        now = time.time()
        elapsed = (now - self.start_time) % CICLO
        t = elapsed / CICLO   # 0..1 dentro del ciclo

        # Determinar fase (0: levantando, 1: avanzando, 2: bajando, 3: soporte)
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

        # Alternar grupo activo al inicio de cada ciclo
        if t < 0.01:
            self.active_group = 'B' if self.active_group == 'A' else 'A'

        # Calcular ángulos para cada pata
        for leg in self.legs.values():
            # Determinar si esta pata pertenece al grupo activo (se mueve)
            in_active = (self.active_group == 'A' and leg.id in self.grupo_a) or \
                        (self.active_group == 'B' and leg.id in self.grupo_b)

            # Centro de cadera: se desplaza según el giro
            # Para las patas izquierdas (impar) y derechas (par) se mueven en direcciones opuestas
            lado = -1 if leg.id % 2 == 1 else 1   # asume impares izquierda, pares derecha
            ang_center = CADERA_ADELANTE[leg.id] + self.angular * 15 * lado

            # Rango de movimiento según velocidad lineal
            range_h = self.linear * RANGO_CADERA
            if self.linear < 0:
                range_h = -range_h

            # Posiciones adelante y atrás relativas al centro
            forward = ang_center + range_h
            backward = ang_center - range_h
            if forward < backward:
                forward, backward = backward, forward

            if in_active:
                # Pata en movimiento (se levanta, avanza y baja)
                if phase == 0:      # levantando
                    v = RODILLA_VERTICAL[leg.id] + (RODILLA_AIRE - RODILLA_VERTICAL[leg.id]) * frac
                    h = backward
                elif phase == 1:    # avanzando en el aire
                    v = RODILLA_AIRE
                    h = backward + (forward - backward) * frac
                elif phase == 2:    # bajando
                    v = RODILLA_AIRE + (RODILLA_VERTICAL[leg.id] - RODILLA_AIRE) * frac
                    h = forward
                else:               # soporte (no debería pasar aquí)
                    v = RODILLA_VERTICAL[leg.id]
                    h = forward
            else:
                # Pata en soporte: solo se mueve la cadera suavemente
                v = RODILLA_VERTICAL[leg.id]
                h = forward + (backward - forward) * t

            leg.set_angles(h, v)

# ========== CONTROL POR TECLADO ==========
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
                linear = 0.5
                angular = 0.0
            elif key == ord('s'):
                linear = -0.5
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

        stdscr.addstr(0, 0, f"Vel: {linear:.2f}  Giro: {angular:.2f}  Grupo: {robot.active_group}")
        stdscr.addstr(1, 0, "W/A/S/D - Q parar - X salir")
        stdscr.refresh()
        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)
