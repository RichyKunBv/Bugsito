#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexápodo - Modo Show
Movimientos impresionantes sin necesidad de caminar
Ideal para SG90 con torque limitado
"""

import time
import curses
import random
from adafruit_servokit import ServoKit

# ========== CONFIGURACIÓN HARDWARE ==========
kit = ServoKit(channels=16, address=0x40)
for ch in range(16):
    kit.servo[ch].set_pulse_width_range(500, 2500)

# Mapeo de patas: (id, canal_cadera, canal_rodilla)
PATAS = {
    1: (0, 1),
    2: (2, 3),
    3: (4, 5),
    4: (6, 7),
    5: (8, 9),
    6: (10, 11),
}

# ========== ÁNGULOS BASE ==========
# Todos los servos parten de 90° (ajústalos si es necesario)
ANG_BASE_CADERA = 90
ANG_BASE_RODILLA = 90

# Ángulos para movimientos (no extremos para evitar sobrecarga)
ANG_LEVANTE = 130       # rodilla levantada
ANG_ABAJO = 80          # rodilla más extendida
ANG_CADERA_IZQ = 70     # cadera izquierda (para balanceo)
ANG_CADERA_DER = 110    # cadera derecha

# ========== CLASE PATA ==========
class Leg:
    def __init__(self, id_, ch_h, ch_v):
        self.id = id_
        self.ch_h = ch_h
        self.ch_v = ch_v
        self.ang_h = ANG_BASE_CADERA
        self.ang_v = ANG_BASE_RODILLA
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
        self.reset()

    def reset(self):
        """Posición neutra: todas las patas a 90°"""
        for leg in self.legs.values():
            leg.set_angles(ANG_BASE_CADERA, ANG_BASE_RODILLA)
        time.sleep(0.5)

    def wave(self):
        """Ola: levanta y baja las patas en secuencia"""
        for leg in self.legs.values():
            leg.set_angles(leg.ang_h, ANG_LEVANTE)
            time.sleep(0.1)
        for leg in self.legs.values():
            leg.set_angles(leg.ang_h, ANG_BASE_RODILLA)
            time.sleep(0.1)

    def dance(self):
        """Baile: balancea el cuerpo moviendo caderas alternadamente"""
        for _ in range(4):
            # Inclinación izquierda
            for leg in self.legs.values():
                if leg.id % 2 == 1:  # patas impares (izquierda)
                    leg.set_angles(ANG_CADERA_IZQ, leg.ang_v)
                else:
                    leg.set_angles(ANG_CADERA_DER, leg.ang_v)
            time.sleep(0.3)
            # Inclinación derecha
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set_angles(ANG_CADERA_DER, leg.ang_v)
                else:
                    leg.set_angles(ANG_CADERA_IZQ, leg.ang_v)
            time.sleep(0.3)
        self.reset()

    def happy(self):
        """Movimiento rápido: agita todas las patas"""
        for _ in range(3):
            for leg in self.legs.values():
                leg.set_angles(leg.ang_h, ANG_LEVANTE)
            time.sleep(0.2)
            for leg in self.legs.values():
                leg.set_angles(leg.ang_h, ANG_BASE_RODILLA)
            time.sleep(0.2)

    def spider_walk(self):
        """Movimiento de patas en parejas (simula caminar sin avanzar)"""
        pares = [(1, 2), (3, 4), (5, 6)]
        for par in pares:
            # Levantar par
            for id_ in par:
                self.legs[id_].set_angles(ANG_BASE_CADERA, ANG_LEVANTE)
            time.sleep(0.3)
            # Bajar par
            for id_ in par:
                self.legs[id_].set_angles(ANG_BASE_CADERA, ANG_BASE_RODILLA)
            time.sleep(0.2)

    def circle(self):
        """Mueve las patas en círculo (cadera)"""
        for ang in range(70, 111, 5):
            for leg in self.legs.values():
                leg.set_angles(ang, leg.ang_v)
            time.sleep(0.05)
        for ang in range(110, 69, -5):
            for leg in self.legs.values():
                leg.set_angles(ang, leg.ang_v)
            time.sleep(0.05)
        self.reset()

    def demo(self, stdscr):
        """Secuencia automática de movimientos"""
        movimientos = [
            ("Ola", self.wave),
            ("Baile", self.dance),
            ("Felicidad", self.happy),
            ("Parejas", self.spider_walk),
            ("Círculo", self.circle),
        ]
        for nombre, funcion in movimientos:
            stdscr.addstr(0, 0, f"  {nombre}  ".center(40))
            stdscr.refresh()
            funcion()
            time.sleep(0.5)
        self.reset()

# ========== INTERFAZ DE CONTROL ==========
def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.clear()

    robot = Robot()
    running = True

    while running:
        key = stdscr.getch()
        if key != -1:
            if key == ord('1'):
                robot.wave()
            elif key == ord('2'):
                robot.dance()
            elif key == ord('3'):
                robot.happy()
            elif key == ord('4'):
                robot.spider_walk()
            elif key == ord('5'):
                robot.circle()
            elif key == ord('0'):
                robot.demo(stdscr)
            elif key == ord('r'):
                robot.reset()
            elif key == ord('q') or key == ord('x'):
                break

        # Mostrar ayuda
        stdscr.addstr(0, 0, "=== HEXÁPODO SHOW ===")
        stdscr.addstr(1, 0, "1: Ola")
        stdscr.addstr(2, 0, "2: Baile")
        stdscr.addstr(3, 0, "3: Felicidad (agitación)")
        stdscr.addstr(4, 0, "4: Caminata de parejas")
        stdscr.addstr(5, 0, "5: Círculo")
        stdscr.addstr(6, 0, "0: Demo automático")
        stdscr.addstr(7, 0, "r: Reset")
        stdscr.addstr(8, 0, "q/x: Salir")
        stdscr.refresh()
        time.sleep(0.05)

    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)
