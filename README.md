# Sistema Integral de Gestión - Software FJ

Sistema orientado a objetos desarrollado en Python con interfaz gráfica tkinter para la gestión de clientes, servicios y reservas de la empresa Software FJ.

**Curso:** Programación 213023
**Universidad:** Universidad Nacional Abierta y a Distancia – UNAD
**Programa:** Ingeniería de Sistemas
**Fase:** 4 – Prácticas Simuladas

---

## Descripción

Aplicación de escritorio que permite gestionar de forma integral los clientes, servicios y reservas de la empresa Software FJ, aplicando los principios de la programación orientada a objetos (abstracción, herencia, polimorfismo y encapsulación) y un manejo robusto de excepciones que garantiza la estabilidad del sistema ante cualquier error.

El sistema **no utiliza bases de datos**; toda la información se gestiona en memoria mediante listas y objetos, y se emplea un archivo de logs (`software_fj_logs.txt`) para el registro de eventos y errores.

---

## Características principales

- Interfaz gráfica organizada en 5 pestañas (Clientes, Servicios, Reservas, Simulación y Logs).
- Validaciones robustas para correo electrónico, teléfono y duración de servicios.
- 3 tipos de servicios especializados: reserva de salas, alquiler de equipos y asesorías.
- 5 excepciones personalizadas con manejo completo (`try/except/else/finally`).
- Encadenamiento de excepciones mediante `raise ... from ...`.
- Registro automático de todos los eventos en archivo de logs.
- Cálculo de costos con IVA y descuentos opcionales (método sobrecargado).
- Módulo de simulación que ejecuta 12 operaciones automatizadas para validar el sistema.

---

## Estructura del sistema

| Clase | Tipo | Responsabilidad |
|-------|------|------------------|
| `EntidadBase` | Abstracta | Define el contrato común de todas las entidades |
| `Cliente` | Concreta | Gestiona los datos del cliente con validaciones |
| `Servicio` | Abstracta | Define el contrato de los servicios |
| `ReservaSala` | Concreta | Servicio de reserva de salas (máx. 12 h) |
| `AlquilerEquipo` | Concreta | Servicio de alquiler de equipos (máx. 72 h) |
| `AsesoriaEspecializada` | Concreta | Servicio de asesoría (máx. 8 h, tarifa premium) |
| `Reserva` | Concreta | Integra cliente, servicio y estado |

---

## Requisitos

- Python 3.8 o superior
- tkinter (incluido por defecto en la instalación estándar de Python)

---

## Ejecución

```bash
python main.py
```

Al ejecutar la aplicación se abrirá la ventana principal con las 5 pestañas disponibles. Para validar el sistema rápidamente, ve a la pestaña **Simulación** y haz clic en **Ejecutar simulación** para ver las 12 operaciones automatizadas.

---

## Autor

**Jonathan Stib Díaz Sabogal**
Código: 1023911433
Grupo: 445

**Tutora:** Martha Liliana Quevedo
