# Proyecto Robot Araña "Bugcito"

## Información más importante del robot

### Origen del Proyecto
Proyecto académico para desarrollar un robot con forma de araña de 6 patas, capaz de moverse mediante servomotores. El objetivo fue simular el movimiento de una araña real mediante el control coordinado de sus patas. Desarrollado en equipo, dividiendo tareas de diseño, programación, electrónica y documentación.

### Materiales utilizados
- Raspberry Pi Zero 2W
- Controlador de servomotores PCA9685
- 12 servomotores
- Módulo regulador de voltaje LM2596
- 2 baterías 18650
- Convertidor lógico bidireccional 5V - 3.3V
- MicroSD

### Software
- Python
- Raspberry Pi OS Lite (Debian Linux 13)

### Diseño del robot
Estructura con 6 patas, cada una controlada por servomotores que permiten movimientos similares a los de una araña real. El microcontrolador (Raspberry Pi) envía las señales para coordinar los motores, permitiendo desplazamiento hacia adelante, atrás y ajustes de equilibrio.

### Diagrama de funcionamiento

![Diagrama de funcionamiento](https://github.com/user-attachments/assets/26734493-2d48-459f-bafa-9686b4682772)

### Problemas encontrados y soluciones
| Problema | Solución |
|----------|----------|
| Sincronización de servomotores | Ajustes en programación y pruebas iterativas |
| Inestabilidad al caminar | Revisión del diseño y código |
| Baterías 9V sin amperaje suficiente | Cambio a LM2596 + 2 baterías 18650 |
| Arduino Uno sin capacidad para 12 servos | Reemplazo por Raspberry Pi Zero 2W |
| Servomotores mal colocados inicialmente | Rearme y colocación correcta |
| Diferencia de voltaje (RPi 3.3V vs servos 5V) | Agregar convertidor lógico bidireccional 5V-3.3V |

### Resultados obtenidos
El robot logró realizar movimientos básicos usando sus seis patas, simulando el desplazamiento de una araña. El proyecto demostró que es posible desarrollar un robot funcional aplicando conocimientos de programación, electrónica y robótica, aunque aún existen oportunidades de mejora.

### Equipo de desarrollo
- Richi Boy
- Ricardo Escamilla

### Conclusión
El proyecto permitió aplicar prácticamente conceptos de robótica, programación y electrónica. El trabajo en equipo fue fundamental para completar cada etapa. Se comprendió mejor el funcionamiento de sistemas robóticos y la coordinación de componentes electrónicos para lograr un objetivo común.

---

## Galería de imágenes

![Robot vista 1](https://github.com/user-attachments/assets/1c1f24ae-d4d3-4377-a69e-774512b2374f)

![Robot vista 2](https://github.com/user-attachments/assets/bc5f074d-9873-4e37-9cab-79708a3ef7e4)

![Robot vista 3](https://github.com/user-attachments/assets/b728e174-c3d8-40e3-b58b-806645a2c846)

![Robot vista 4](https://github.com/user-attachments/assets/1340bb9a-fc51-4831-9ee3-0cc1bb5690c2)

![Robot vista 5](https://github.com/user-attachments/assets/7aeee6e4-6bc4-47f5-8ac0-fa7cd8ef36a3)

![Bugcito fachero](https://github.com/user-attachments/assets/1cca7de6-ba7b-439a-b3c5-c8574f49f0e8)
