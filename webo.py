#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hexápodo con marcha en trípode suave y efectos especiales
Diseñado para SG90 con bajo torque: movimientos elegantes y estables
Controles:
  W/A/S/D  : caminar / girar
  T        : modo demostración automático
  R        : reset a posición neutra
  V        : "ola" con las patas (wave)
  B        : bailecito (dance)
  Q        : detener movimiento
  X        : salir
"""

import time
import curses
import math
from adafruit_servokit import ServoKit

# ==================== CONFIGURACIÓN ====================
kit = ServoKit(channels=16, address=0x40)
for ch in range(16):
    kit.servo[ch].set_pulse_width_range(500, 2500)

# Mapeo de patas: (id, canal_h, canal_v, lado)
# lado: -1 izquierda, 1 derecha (ajústalo según tu montaje)
PATAS = {
    1: (0, 1, -1),
    2: (2, 3, 1),
    3: (4, 5, -1),
    4: (6, 7, 1),
    5: (8, 9, -1),
    6: (10, 11, 1),
}

# Grupos de trípode (dos grupos que se alternan)
# Configuración clásica: grupo A = patas 1,4,5 ; grupo B = 2,3,6
GRUPO_A = [1, 4, 5]
GRUPO_B = [2, 3, 6]

# Ángulos de referencia (CALIBRA ESTOS CON TU ROBOT)
ANG_CADERA_CENTRO = 90          # cadera mirando hacia adelante
ANG_RODILLA_SOPORTE = 85        # rodilla en soporte (casi vertical)
ANG_RODILLA_AIRE = 135          # rodilla levantada

# Parámetros de marcha
CICLO = 1.5                     # segundos por ciclo completo (más lento = más torque)
T_LEVANTAR = 0.25
T_AVANZAR = 0.4
T_BAJAR = 0.25
# El resto es soporte

RANGO_CADERA = 25               # desplazamiento máximo de cadera (grados)
GIRO_MAX = 15                   # máximo desplazamiento por giro (grados)

# ==================== CLASE LEG ====================
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

# ==================== CLASE ROBOT ====================
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
        self.demo_mode = False
        self.demo_step = 0
        self.demo_start = 0
        
        # Posición neutra
        self.reset()
    
    def reset(self):
        """Vuelve a posición neutra"""
        for leg in self.legs.values():
            leg.set_angles(ANG_CADERA_CENTRO, ANG_RODILLA_SOPORTE)
        self.linear = 0.0
        self.angular = 0.0
        time.sleep(0.5)
    
    def set_speed(self, linear, angular):
        self.linear = max(-1.0, min(1.0, linear))
        self.angular = max(-1.0, min(1.0, angular))
    
    def wave(self):
        """Ola con las patas: levanta y baja en secuencia"""
        for leg in self.legs.values():
            leg.set_angles(leg.ang_h, ANG_RODILLA_AIRE)
            time.sleep(0.1)
        for leg in self.legs.values():
            leg.set_angles(leg.ang_h, ANG_RODILLA_SOPORTE)
            time.sleep(0.1)
    
    def dance(self):
        """Baile: balancea el cuerpo moviendo caderas"""
        for _ in range(3):
            for leg in self.legs.values():
                # Mover cadera hacia un lado
                leg.set_angles(ANG_CADERA_CENTRO + 20 * leg.lado, leg.ang_v)
            time.sleep(0.3)
            for leg in self.legs.values():
                leg.set_angles(ANG_CADERA_CENTRO - 20 * leg.lado, leg.ang_v)
            time.sleep(0.3)
        self.reset()
    
    def update(self):
        """Actualiza la posición de todas las patas según el tiempo y velocidad"""
        if self.demo_mode:
            self._update_demo()
            return
        
        now = time.time()
        elapsed = (now - self.start_time) % CICLO
        t = elapsed / CICLO
        
        # Fase y factor de interpolación con easing (curva suave)
        if t < T_LEVANTAR / CICLO:
            phase = 0
            frac = t / (T_LEVANTAR / CICLO)
            # easing ease-out
            frac = 1 - (1 - frac) ** 2
        elif t < (T_LEVANTAR + T_AVANZAR) / CICLO:
            phase = 1
            frac = (t - T_LEVANTAR/CICLO) / (T_AVANZAR / CICLO)
            # easing linear
        elif t < (T_LEVANTAR + T_AVANZAR + T_BAJAR) / CICLO:
            phase = 2
            frac = (t - (T_LEVANTAR+T_AVANZAR)/CICLO) / (T_BAJAR / CICLO)
            # easing ease-in
            frac = frac ** 2
        else:
            phase = 3
            frac = (t - (T_LEVANTAR+T_AVANZAR+T_BAJAR)/CICLO) / ((CICLO - T_LEVANTAR - T_AVANZAR - T_BAJAR)/CICLO)
            frac = frac  # linear
        
        # Alternar grupo activo al inicio del ciclo
        if t < 0.01:
            self.active_group = 'B' if self.active_group == 'A' else 'A'
        
        # Calcular para cada pata
        for leg in self.legs.values():
            in_active = (self.active_group == 'A' and leg.id in self.grupo_a) or \
                        (self.active_group == 'B' and leg.id in self.grupo_b)
            
            # Ángulo centro de cadera con efecto de giro
            ang_center = ANG_CADERA_CENTRO + self.angular * GIRO_MAX * leg.lado
            
            # Rango de movimiento según velocidad lineal
            range_h = self.linear * RANGO_CADERA
            if self.linear < 0:
                range_h = -range_h
            
            forward = ang_center + range_h
            backward = ang_center - range_h
            if forward < backward:
                forward, backward = backward, forward
            
            if in_active:
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
                v = ANG_RODILLA_SOPORTE
                # Cadera se mueve suavemente durante todo el ciclo
                h = forward + (backward - forward) * t
            
            leg.set_angles(h, v)
    
    def _update_demo(self):
        """Modo demostración: secuencia automática de movimientos"""
        now = time.time()
        elapsed = now - self.demo_start
        if elapsed < 5:
            # Avanzar lento
            self.set_speed(0.4, 0)
        elif elapsed < 10:
            # Girar izquierda
            self.set_speed(0, 0.5)
        elif elapsed < 15:
            # Girar derecha
            self.set_speed(0, -0.5)
        elif elapsed < 20:
            # Retroceder
            self.set_speed(-0.3, 0)
        elif elapsed < 25:
            # Ola
            self.set_speed(0, 0)
            self.wave()
            self.demo_start = now  # reiniciar temporizador para no repetir muchas veces
        elif elapsed < 30:
            # Baile
            self.set_speed(0, 0)
            self.dance()
            self.demo_start = now
        else:
            # Reiniciar demo
            self.demo_mode = False
            self.reset()
        # Llamar a update normal para mover según velocidades
        self.update()

# ==================== INTERFAZ TECLADO ====================
def main(stdscr):
    curses.cbreak()
    stdscr.nodelay(True)
    stdscr.clear()
    
    robot = Robot()
    linear = 0.0
    angular = 0.0
    last_key_time = 0
    demo_toggle_time = 0
    
    while True:
        key = stdscr.getch()
        now = time.time()
        
        # Evitar spam de teclas
        if key != -1:
            if key == ord('w'):
                linear = 0.5
                angular = 0.0
                robot.demo_mode = False
            elif key == ord('s'):
                linear = -0.5
                angular = 0.0
                robot.demo_mode = False
            elif key == ord('a'):
                linear = 0.0
                angular = 0.5
                robot.demo_mode = False
            elif key == ord('d'):
                linear = 0.0
                angular = -0.5
                robot.demo_mode = False
            elif key == ord('q'):
                linear = 0.0
                angular = 0.0
                robot.demo_mode = False
            elif key == ord('r'):
                robot.reset()
                linear = 0.0
                angular = 0.0
                robot.demo_mode = False
            elif key == ord('v'):
                robot.wave()
                robot.demo_mode = False
            elif key == ord('b'):
                robot.dance()
                robot.demo_mode = False
            elif key == ord('t'):
                # Alternar modo demo
                if not robot.demo_mode:
                    robot.demo_mode = True
                    robot.demo_start = now
                    linear = 0.0
                    angular = 0.0
                else:
                    robot.demo_mode = False
                    robot.reset()
            elif key == ord('x'):
                break
        
        robot.set_speed(linear, angular)
        robot.update()
        
        # Mostrar información
        status = "DEMO" if robot.demo_mode else "MANUAL"
        stdscr.addstr(0, 0, f"Hexápodo | Modo: {status} | Vel: {linear:.2f} | Giro: {angular:.2f}   ")
        stdscr.addstr(1, 0, "W/A/S/D: caminar/girar | T: demo | R: reset | V: ola | B: baile | Q: parar | X: salir")
        stdscr.refresh()
        
        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)
