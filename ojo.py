#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNICOP SHOW – Hexápodo de élite
20 movimientos + modo demo + modo aleatorio
Diseñado para SG90 con movimientos seguros y elegantes
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
BASE_CADERA = 90
BASE_RODILLA = 90

# Límites seguros para SG90 (no forzar extremos)
MAX_CADERA = 70     # mínimo 70°
MIN_CADERA = 110    # máximo 110° (rango de ±20° desde 90)
MAX_RODILLA_UP = 130   # levantar pata
MAX_RODILLA_DOWN = 70  # extender pata (cuidado)

# ========== CLASE PATA ==========
class Leg:
    def __init__(self, id_, ch_h, ch_v):
        self.id = id_
        self.ch_h = ch_h
        self.ch_v = ch_v
        self.h = BASE_CADERA
        self.v = BASE_RODILLA
        self._update()

    def _update(self):
        kit.servo[self.ch_h].angle = self.h
        kit.servo[self.ch_v].angle = self.v

    def set(self, h=None, v=None):
        if h is not None:
            self.h = max(MAX_CADERA, min(MIN_CADERA, h))
        if v is not None:
            self.v = max(MAX_RODILLA_DOWN, min(MAX_RODILLA_UP, v))
        self._update()

# ========== CLASE ROBOT ==========
class Robot:
    def __init__(self):
        self.legs = {}
        for id_, (ch_h, ch_v) in PATAS.items():
            self.legs[id_] = Leg(id_, ch_h, ch_v)
        self.reset()

    def reset(self):
        for leg in self.legs.values():
            leg.set(BASE_CADERA, BASE_RODILLA)
        time.sleep(0.3)

    # ---------- MOVIMIENTOS BÁSICOS ----------
    def wave(self, reverse=False):
        """Ola simple"""
        order = list(self.legs.keys())
        if reverse:
            order.reverse()
        for id_ in order:
            self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.08)
        for id_ in order:
            self.legs[id_].set(v=BASE_RODILLA)
            time.sleep(0.08)

    def wave_double(self):
        """Ola doble (sube y baja rápido)"""
        for _ in range(2):
            self.wave()
        self.reset()

    def wiggle(self):
        """Sacude todas las patas"""
        for _ in range(3):
            for leg in self.legs.values():
                leg.set(v=MAX_RODILLA_UP)
            time.sleep(0.1)
            for leg in self.legs.values():
                leg.set(v=BASE_RODILLA)
            time.sleep(0.1)

    def side_rock(self):
        """Balanceo lateral (cadera)"""
        for _ in range(3):
            for leg in self.legs.values():
                if leg.id % 2 == 1:  # impares izquierda
                    leg.set(h=MAX_CADERA)
                else:
                    leg.set(h=MIN_CADERA)
            time.sleep(0.3)
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MIN_CADERA)
                else:
                    leg.set(h=MAX_CADERA)
            time.sleep(0.3)
        self.reset()

    def twist(self):
        """Giro de torso (alternar cadera izquierda/derecha)"""
        for _ in range(4):
            # Patas izquierdas adelante, derechas atrás
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MAX_CADERA)
                else:
                    leg.set(h=MIN_CADERA)
            time.sleep(0.2)
            # Patas izquierdas atrás, derechas adelante
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MIN_CADERA)
                else:
                    leg.set(h=MAX_CADERA)
            time.sleep(0.2)
        self.reset()

    def circle_dance(self):
        """Círculo suave de caderas"""
        for ang in range(MAX_CADERA, MIN_CADERA+1, 5):
            for leg in self.legs.values():
                leg.set(h=ang)
            time.sleep(0.03)
        for ang in range(MIN_CADERA, MAX_CADERA-1, -5):
            for leg in self.legs.values():
                leg.set(h=ang)
            time.sleep(0.03)
        self.reset()

    def spider_crawl(self):
        """Marcha en trípode en el sitio (movimiento de patas)"""
        # Grupo A: patas 1,4,5 ; Grupo B: 2,3,6
        grupo_a = [1,4,5]
        grupo_b = [2,3,6]
        for _ in range(2):
            # Levantar grupo A, bajar grupo B
            for id_ in grupo_a:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            for id_ in grupo_b:
                self.legs[id_].set(v=BASE_RODILLA)
            time.sleep(0.4)
            # Levantar grupo B, bajar grupo A
            for id_ in grupo_b:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            for id_ in grupo_a:
                self.legs[id_].set(v=BASE_RODILLA)
            time.sleep(0.4)
        self.reset()

    def wave_3d(self):
        """Ola con movimiento de caderas (3D)"""
        # Subir patas de atrás hacia adelante
        order = [6,5,4,3,2,1]
        for id_ in order:
            self.legs[id_].set(v=MAX_RODILLA_UP, h=MIN_CADERA)
            time.sleep(0.08)
        for id_ in order:
            self.legs[id_].set(v=BASE_RODILLA, h=BASE_CADERA)
            time.sleep(0.08)

    def happy_dance(self):
        """Danza rápida con rodillas"""
        for _ in range(6):
            for leg in self.legs.values():
                leg.set(v=MAX_RODILLA_UP)
            time.sleep(0.1)
            for leg in self.legs.values():
                leg.set(v=MAX_RODILLA_DOWN)
            time.sleep(0.1)
        self.reset()

    def praying(self):
        """Postura de mantis: patas delanteras elevadas"""
        for id_ in [1,2]:  # patas delanteras
            self.legs[id_].set(v=MAX_RODILLA_UP)
        time.sleep(1)
        for id_ in [1,2]:
            self.legs[id_].set(v=BASE_RODILLA)
        self.reset()

    def crab_walk(self):
        """Movimiento lateral: patas izquierdas adelante, derechas atrás"""
        for _ in range(2):
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MAX_CADERA)
                else:
                    leg.set(h=MIN_CADERA)
            time.sleep(0.5)
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MIN_CADERA)
                else:
                    leg.set(h=MAX_CADERA)
            time.sleep(0.5)
        self.reset()

    def lightning(self):
        """Movimiento rápido en zigzag"""
        for _ in range(3):
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MAX_CADERA, v=MAX_RODILLA_UP)
                else:
                    leg.set(h=MIN_CADERA, v=MAX_RODILLA_UP)
            time.sleep(0.2)
            for leg in self.legs.values():
                if leg.id % 2 == 1:
                    leg.set(h=MIN_CADERA, v=BASE_RODILLA)
                else:
                    leg.set(h=MAX_CADERA, v=BASE_RODILLA)
            time.sleep(0.2)
        self.reset()

    def helicopter(self):
        """Giro circular de caderas"""
        for ang in range(MAX_CADERA, MIN_CADERA+1, 3):
            for leg in self.legs.values():
                leg.set(h=ang)
            time.sleep(0.02)
        for ang in range(MIN_CADERA, MAX_CADERA-1, -3):
            for leg in self.legs.values():
                leg.set(h=ang)
            time.sleep(0.02)
        self.reset()

    def roll_call(self):
        """Levantar patas en pares secuenciales"""
        pares = [(1,2), (3,4), (5,6)]
        for par in pares:
            for id_ in par:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.3)
        for par in pares:
            for id_ in par:
                self.legs[id_].set(v=BASE_RODILLA)
            time.sleep(0.3)

    def bounce(self):
        """Rebote: subir y bajar todas las patas al unísono"""
        for _ in range(3):
            for leg in self.legs.values():
                leg.set(v=MAX_RODILLA_UP)
            time.sleep(0.2)
            for leg in self.legs.values():
                leg.set(v=BASE_RODILLA)
            time.sleep(0.2)

    def crawl_slow(self):
        """Marcha lenta en el sitio"""
        grupo_a = [1,4,5]
        grupo_b = [2,3,6]
        for _ in range(2):
            for id_ in grupo_a:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.5)
            for id_ in grupo_a:
                self.legs[id_].set(v=BASE_RODILLA)
            for id_ in grupo_b:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.5)
            for id_ in grupo_b:
                self.legs[id_].set(v=BASE_RODILLA)
        self.reset()

    def wave_alternating(self):
        """Ola alterna: izquierda-derecha"""
        for _ in range(2):
            # Levantar patas impares
            for id_ in [1,3,5]:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.2)
            for id_ in [1,3,5]:
                self.legs[id_].set(v=BASE_RODILLA)
            # Levantar patas pares
            for id_ in [2,4,6]:
                self.legs[id_].set(v=MAX_RODILLA_UP)
            time.sleep(0.2)
            for id_ in [2,4,6]:
                self.legs[id_].set(v=BASE_RODILLA)

    def party(self):
        """Fiesta: combinación de movimientos rápidos"""
        for _ in range(2):
            self.wave()
            self.side_rock()
            self.wiggle()
        self.reset()

    # ---------- DEMO AUTOMÁTICO ----------
    def demo(self, stdscr):
        """Secuencia completa de todos los movimientos"""
        movimientos = [
            ("Ola", self.wave),
            ("Ola doble", self.wave_double),
            ("Sacudida", self.wiggle),
            ("Balanceo", self.side_rock),
            ("Twist", self.twist),
            ("Círculo", self.circle_dance),
            ("Caminata", self.spider_crawl),
            ("Ola 3D", self.wave_3d),
            ("Danza feliz", self.happy_dance),
            ("Mantis", self.praying),
            ("Cangrejo", self.crab_walk),
            ("Relámpago", self.lightning),
            ("Helicóptero", self.helicopter),
            ("Llamada", self.roll_call),
            ("Rebote", self.bounce),
            ("Marcha lenta", self.crawl_slow),
            ("Ola alterna", self.wave_alternating),
            ("Fiesta", self.party),
        ]
        for nombre, funcion in movimientos:
            stdscr.clear()
            stdscr.addstr(0, 0, f"🎬 {nombre} 🎬".center(40))
            stdscr.refresh()
            funcion()
            time.sleep(0.3)
        self.reset()
        stdscr.clear()
        stdscr.addstr(0, 0, "¡FIN DEL ESPECTÁCULO!".center(40))
        stdscr.refresh()
        time.sleep(1)

    def random_mode(self, stdscr, duration=30):
        """Modo aleatorio: elige movimientos al azar durante 'duration' segundos"""
        movimientos = [
            self.wave, self.wave_double, self.wiggle, self.side_rock,
            self.twist, self.circle_dance, self.spider_crawl, self.wave_3d,
            self.happy_dance, self.praying, self.crab_walk, self.lightning,
            self.helicopter, self.roll_call, self.bounce, self.crawl_slow,
            self.wave_alternating, self.party
        ]
        start = time.time()
        while time.time() - start < duration:
            move = random.choice(movimientos)
            stdscr.clear()
            stdscr.addstr(0, 0, f"🎲 ALEATORIO: {move.__name__} 🎲".center(40))
            stdscr.refresh()
            move()
            time.sleep(random.uniform(0.5, 1.5))
        self.reset()

# ========== INTERFAZ TECLADO ==========
def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.clear()

    robot = Robot()
    help_text = [
        "=== UNICOP SHOW ===",
        "1: Ola              2: Ola doble",
        "3: Sacudida         4: Balanceo",
        "5: Twist            6: Círculo",
        "7: Caminata         8: Ola 3D",
        "9: Danza feliz      0: Mantis",
        "q: Cangrejo         w: Relámpago",
        "e: Helicóptero      r: Llamada",
        "t: Rebote           y: Marcha lenta",
        "u: Ola alterna      i: Fiesta",
        "d: Demo automático  a: Modo aleatorio (30s)",
        "s: Reset            x: Salir",
    ]

    while True:
        # Mostrar ayuda
        stdscr.clear()
        for i, line in enumerate(help_text):
            stdscr.addstr(i, 0, line)
        stdscr.refresh()

        key = stdscr.getch()
        if key != -1:
            if key == ord('1'):
                robot.wave()
            elif key == ord('2'):
                robot.wave_double()
            elif key == ord('3'):
                robot.wiggle()
            elif key == ord('4'):
                robot.side_rock()
            elif key == ord('5'):
                robot.twist()
            elif key == ord('6'):
                robot.circle_dance()
            elif key == ord('7'):
                robot.spider_crawl()
            elif key == ord('8'):
                robot.wave_3d()
            elif key == ord('9'):
                robot.happy_dance()
            elif key == ord('0'):
                robot.praying()
            elif key == ord('q'):
                robot.crab_walk()
            elif key == ord('w'):
                robot.lightning()
            elif key == ord('e'):
                robot.helicopter()
            elif key == ord('r'):
                robot.roll_call()
            elif key == ord('t'):
                robot.bounce()
            elif key == ord('y'):
                robot.crawl_slow()
            elif key == ord('u'):
                robot.wave_alternating()
            elif key == ord('i'):
                robot.party()
            elif key == ord('d'):
                robot.demo(stdscr)
            elif key == ord('a'):
                robot.random_mode(stdscr)
            elif key == ord('s'):
                robot.reset()
            elif key == ord('x'):
                break

        time.sleep(0.05)

if __name__ == "__main__":
    curses.wrapper(main)
