"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación 213023 - UNAD
Interfaz gráfica desarrollada con tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import datetime
from abc import ABC, abstractmethod

# ============================================================
# CONFIGURACIÓN DEL ARCHIVO DE LOGS
# ============================================================
_log_handler = logging.FileHandler("software_fj_logs.txt", encoding="utf-8")
_log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logging.getLogger().addHandler(_log_handler)
logging.getLogger().setLevel(logging.INFO)

def registrar_log(nivel, mensaje):
    """Registra un mensaje en el archivo de logs."""
    if nivel == "info":
        logging.info(mensaje)
    elif nivel == "error":
        logging.error(mensaje)
    elif nivel == "warning":
        logging.warning(mensaje)


# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================

class ErrorClienteInvalido(Exception):
    """Excepción para datos de cliente inválidos."""
    pass

class ErrorServicioNoDisponible(Exception):
    """Excepción cuando un servicio no está disponible."""
    pass

class ErrorReservaInvalida(Exception):
    """Excepción para reservas con datos incorrectos."""
    pass

class ErrorDuracionInvalida(Exception):
    """Excepción para duraciones fuera de rango."""
    pass

class ErrorPagoInvalido(Exception):
    """Excepción para errores en el procesamiento de pagos."""
    pass


# ============================================================
# CLASE ABSTRACTA BASE
# ============================================================

class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""

    def __init__(self, id_entidad, nombre):
        if not id_entidad or not isinstance(id_entidad, str):
            raise ValueError("El ID debe ser una cadena no vacía.")
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        self._id_entidad = id_entidad
        self._nombre = nombre

    @abstractmethod
    def describir(self):
        """Método abstracto que cada clase debe implementar."""
        pass

    @property
    def id_entidad(self):
        return self._id_entidad

    @property
    def nombre(self):
        return self._nombre


# ============================================================
# CLASE CLIENTE
# ============================================================

class Cliente(EntidadBase):
    """Clase que representa un cliente de Software FJ con validaciones robustas."""

    def __init__(self, id_cliente, nombre, email, telefono):
        try:
            super().__init__(id_cliente, nombre)
            self._email = self._validar_email(email)
            self._telefono = self._validar_telefono(telefono)
            self._activo = True
            registrar_log("info", f"Cliente creado: {nombre} ({id_cliente})")
        except (ErrorClienteInvalido, ValueError) as e:
            registrar_log("error", f"Error al crear cliente {nombre}: {e}")
            raise

    def _validar_email(self, email):
        """Valida que el email tenga formato correcto."""
        if not email or "@" not in email or "." not in email:
            raise ErrorClienteInvalido(f"Email inválido: '{email}'. Debe contener '@' y '.'")
        return email

    def _validar_telefono(self, telefono):
        """Valida que el teléfono sea numérico con mínimo 7 dígitos."""
        telefono_str = str(telefono).replace(" ", "").replace("-", "")
        if not telefono_str.isdigit() or len(telefono_str) < 7:
            raise ErrorClienteInvalido(f"Teléfono inválido: '{telefono}'. Mínimo 7 dígitos.")
        return telefono_str

    def describir(self):
        estado = "Activo" if self._activo else "Inactivo"
        return f"{self._id_entidad} | {self._nombre} | {self._email} | {self._telefono} | {estado}"

    @property
    def email(self):
        return self._email

    @property
    def activo(self):
        return self._activo

    def desactivar(self):
        """Desactiva el cliente en el sistema."""
        self._activo = False
        registrar_log("warning", f"Cliente desactivado: {self._nombre}")


# ============================================================
# CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(EntidadBase, ABC):
    """Clase abstracta que representa un servicio de Software FJ."""

    def __init__(self, id_servicio, nombre, precio_base, disponible=True):
        super().__init__(id_servicio, nombre)
        if precio_base <= 0:
            raise ErrorServicioNoDisponible(f"Precio base debe ser mayor a 0. Recibido: {precio_base}")
        self._precio_base = precio_base
        self._disponible = disponible

    @abstractmethod
    def calcular_costo(self, duracion_horas):
        """Calcula el costo base según la duración."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion_horas):
        """Valida parámetros antes de crear una reserva."""
        pass

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"{self._id_entidad} | {self._nombre} | ${self._precio_base:,.0f}/h | {estado}"

    @property
    def disponible(self):
        return self._disponible

    @property
    def precio_base(self):
        return self._precio_base

    def calcular_costo_total(self, duracion_horas, aplicar_impuesto=False,
                              descuento=0.0, participantes=1):
        """
        Método sobrecargado: calcula costo con impuestos,
        descuentos y participantes como parámetros opcionales.
        """
        try:
            costo = self.calcular_costo(duracion_horas)
            if descuento < 0 or descuento > 1:
                raise ErrorPagoInvalido(f"Descuento debe estar entre 0 y 1. Recibido: {descuento}")
            costo = costo * (1 - descuento)
            if participantes > 1:
                costo = costo * participantes
            if aplicar_impuesto:
                costo = costo * 1.19  # IVA 19%
            return round(costo, 2)
        except ErrorPagoInvalido as e:
            registrar_log("error", f"Error en cálculo de costo: {e}")
            raise


# ============================================================
# SERVICIOS ESPECIALIZADOS
# ============================================================

class ReservaSala(Servicio):
    """Servicio especializado: reserva de salas de reuniones."""

    def __init__(self, id_servicio, nombre, precio_base, capacidad_maxima):
        super().__init__(id_servicio, nombre, precio_base)
        self._capacidad_maxima = capacidad_maxima

    def calcular_costo(self, duracion_horas):
        """Costo = precio_base * horas."""
        self.validar_parametros(duracion_horas)
        return self._precio_base * duracion_horas

    def validar_parametros(self, duracion_horas):
        """Sala: mínimo 1h, máximo 12h."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorDuracionInvalida(f"Duración inválida: {duracion_horas}.")
        if duracion_horas > 12:
            raise ErrorDuracionInvalida(f"Máximo 12h para sala. Solicitado: {duracion_horas}h")

    def describir(self):
        return super().describir() + f" | Cap: {self._capacidad_maxima} personas | Sala"


class AlquilerEquipo(Servicio):
    """Servicio especializado: alquiler de equipos tecnológicos."""

    def __init__(self, id_servicio, nombre, precio_base, tipo_equipo):
        super().__init__(id_servicio, nombre, precio_base)
        self._tipo_equipo = tipo_equipo

    def calcular_costo(self, duracion_horas):
        """Costo = (precio_base * horas) + cargo fijo de manipulación."""
        self.validar_parametros(duracion_horas)
        return (self._precio_base * duracion_horas) + 15000

    def validar_parametros(self, duracion_horas):
        """Equipo: máximo 72h."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorDuracionInvalida(f"Duración inválida: {duracion_horas}.")
        if duracion_horas > 72:
            raise ErrorDuracionInvalida(f"Máximo 72h para equipo. Solicitado: {duracion_horas}h")

    def describir(self):
        return super().describir() + f" | {self._tipo_equipo} | Equipo"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: asesoría por expertos con tarifa premium."""

    def __init__(self, id_servicio, nombre, precio_base, area):
        super().__init__(id_servicio, nombre, precio_base)
        self._area = area

    def calcular_costo(self, duracion_horas):
        """Costo = precio_base * horas * 1.3 (tarifa premium 30%)."""
        self.validar_parametros(duracion_horas)
        return self._precio_base * duracion_horas * 1.3

    def validar_parametros(self, duracion_horas):
        """Asesoría: máximo 8h."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorDuracionInvalida(f"Duración inválida: {duracion_horas}.")
        if duracion_horas > 8:
            raise ErrorDuracionInvalida(f"Máximo 8h para asesoría. Solicitado: {duracion_horas}h")

    def describir(self):
        return super().describir() + f" | {self._area} | Asesoría"


# ============================================================
# CLASE RESERVA
# ============================================================

class Reserva:
    """
    Clase que integra cliente, servicio, duración y estado.
    Implementa confirmación, cancelación y pago con manejo completo de excepciones.
    """

    def __init__(self, id_reserva, cliente, servicio, duracion_horas):
        try:
            if not isinstance(cliente, Cliente):
                raise ErrorReservaInvalida("Cliente no válido.")
            if not cliente.activo:
                raise ErrorReservaInvalida(f"Cliente {cliente.nombre} está inactivo.")
            if not isinstance(servicio, Servicio):
                raise ErrorReservaInvalida("Servicio no válido.")
            if not servicio.disponible:
                raise ErrorServicioNoDisponible(f"Servicio '{servicio.nombre}' no disponible.")
            servicio.validar_parametros(duracion_horas)

            self._id_reserva = id_reserva
            self._cliente = cliente
            self._servicio = servicio
            self._duracion_horas = duracion_horas
            self._estado = "pendiente"
            self._fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self._costo_total = servicio.calcular_costo(duracion_horas)

            registrar_log("info",
                f"Reserva {id_reserva}: {cliente.nombre} / "
                f"{servicio.nombre} / {duracion_horas}h / ${self._costo_total:,.0f}")

        except (ErrorReservaInvalida, ErrorServicioNoDisponible, ErrorDuracionInvalida) as e:
            registrar_log("error", f"Error reserva {id_reserva}: {e}")
            raise

    def confirmar(self):
        """Confirma la reserva si está pendiente."""
        try:
            if self._estado != "pendiente":
                raise ErrorReservaInvalida(
                    f"Solo se confirman reservas pendientes. Estado: {self._estado}")
            self._estado = "confirmada"
            registrar_log("info", f"Reserva {self._id_reserva} confirmada.")
        except ErrorReservaInvalida as e:
            registrar_log("error", f"Error confirmar {self._id_reserva}: {e}")
            raise

    def cancelar(self):
        """Cancela la reserva si no está completada."""
        try:
            if self._estado == "completada":
                raise ErrorReservaInvalida("No se puede cancelar una reserva completada.")
            if self._estado == "cancelada":
                raise ErrorReservaInvalida("La reserva ya está cancelada.")
            self._estado = "cancelada"
            registrar_log("warning", f"Reserva {self._id_reserva} cancelada.")
        except ErrorReservaInvalida as e:
            registrar_log("error", f"Error cancelar {self._id_reserva}: {e}")
            raise

    def procesar_pago(self, monto_pagado, aplicar_impuesto=False, descuento=0.0):
        """
        Procesa el pago usando try/except/else/finally.
        Encadena excepciones de pago hacia ErrorReservaInvalida.
        """
        try:
            if self._estado != "confirmada":
                raise ErrorPagoInvalido(
                    f"Solo se pagan reservas confirmadas. Estado: {self._estado}")
            costo_final = self._servicio.calcular_costo_total(
                self._duracion_horas,
                aplicar_impuesto=aplicar_impuesto,
                descuento=descuento)
            if monto_pagado < costo_final:
                raise ErrorPagoInvalido(
                    f"Monto insuficiente. Requerido: ${costo_final:,.0f}, "
                    f"Recibido: ${monto_pagado:,.0f}")
        except ErrorPagoInvalido as e:
            registrar_log("error", f"Error pago {self._id_reserva}: {e}")
            raise ErrorReservaInvalida(f"Fallo en el pago: {e}") from e
        else:
            # Solo si no hubo excepción
            cambio = monto_pagado - costo_final
            self._estado = "completada"
            registrar_log("info",
                f"Pago OK {self._id_reserva}. "
                f"Costo: ${costo_final:,.0f} | Cambio: ${cambio:,.0f}")
            return cambio, costo_final
        finally:
            # Siempre se ejecuta
            registrar_log("info", f"Procesamiento de pago finalizado: {self._id_reserva}")

    def describir(self):
        return (f"{self._id_reserva} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._duracion_horas}h | "
                f"{self._estado} | ${self._costo_total:,.0f} | {self._fecha}")

    @property
    def id_reserva(self):
        return self._id_reserva

    @property
    def estado(self):
        return self._estado

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion(self):
        return self._duracion_horas


# ============================================================
# INTERFAZ GRÁFICA - TKINTER
# ============================================================

COLORES = {
    "primario":   "#1a73e8",
    "secundario": "#f1f3f4",
    "exito":      "#34a853",
    "error":      "#ea4335",
    "advertencia":"#fbbc04",
    "texto":      "#202124",
    "blanco":     "#ffffff",
    "gris":       "#5f6368",
    "borde":      "#dadce0"
}


class SistemaFJ:
    """Clase principal de la interfaz gráfica del sistema Software FJ."""

    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ — Sistema de Gestión")
        self.root.geometry("960x660")
        self.root.configure(bg=COLORES["secundario"])
        self.root.resizable(True, True)

        # Datos del sistema
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self._contador_clientes = 1
        self._contador_reservas = 1

        self._cargar_servicios_default()
        self._construir_header()
        self._construir_tabs()

    def _cargar_servicios_default(self):
        """Carga servicios predefinidos del sistema."""
        try:
            self.servicios.append(ReservaSala("S001", "Sala Innovación", 50000, 10))
            self.servicios.append(ReservaSala("S002", "Sala Conferencias", 80000, 20))
            self.servicios.append(AlquilerEquipo("S003", "Laptop HP ProBook", 20000, "Laptop"))
            self.servicios.append(AlquilerEquipo("S004", "Proyector Epson", 15000, "Proyector"))
            self.servicios.append(AsesoriaEspecializada("S005", "Asesoría en IA", 80000, "Inteligencia Artificial"))
            self.servicios.append(AsesoriaEspecializada("S006", "Asesoría Ciberseguridad", 90000, "Ciberseguridad"))
        except Exception as e:
            registrar_log("error", f"Error cargando servicios: {e}")

    # ── HEADER ────────────────────────────────────────────────────

    def _construir_header(self):
        header = tk.Frame(self.root, bg=COLORES["primario"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚙  Software FJ — Sistema de Gestión",
                 font=("Segoe UI", 15, "bold"),
                 bg=COLORES["primario"], fg=COLORES["blanco"]
                 ).pack(side="left", padx=20, pady=15)
        tk.Label(header, text="Programación 213023 · UNAD",
                 font=("Segoe UI", 9),
                 bg=COLORES["primario"], fg="#c5d8fb"
                 ).pack(side="right", padx=20)

    # ── TABS ──────────────────────────────────────────────────────

    def _construir_tabs(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=COLORES["secundario"], borderwidth=0)
        style.configure("TNotebook.Tab",
                         font=("Segoe UI", 10, "bold"), padding=[16, 8],
                         background=COLORES["borde"], foreground=COLORES["gris"])
        style.map("TNotebook.Tab",
                   background=[("selected", COLORES["blanco"])],
                   foreground=[("selected", COLORES["primario"])])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_clientes   = tk.Frame(self.notebook, bg=COLORES["blanco"])
        self.tab_servicios  = tk.Frame(self.notebook, bg=COLORES["blanco"])
        self.tab_reservas   = tk.Frame(self.notebook, bg=COLORES["blanco"])
        self.tab_simulacion = tk.Frame(self.notebook, bg=COLORES["blanco"])
        self.tab_logs       = tk.Frame(self.notebook, bg=COLORES["blanco"])

        self.notebook.add(self.tab_clientes,   text="👤  Clientes")
        self.notebook.add(self.tab_servicios,  text="🛎  Servicios")
        self.notebook.add(self.tab_reservas,   text="📅  Reservas")
        self.notebook.add(self.tab_simulacion, text="🧪  Simulación")
        self.notebook.add(self.tab_logs,       text="📋  Logs")

        self._construir_tab_clientes()
        self._construir_tab_servicios()
        self._construir_tab_reservas()
        self._construir_tab_simulacion()
        self._construir_tab_logs()

    # ── TAB CLIENTES ──────────────────────────────────────────────

    def _construir_tab_clientes(self):
        tab = self.tab_clientes

        # Formulario izquierdo
        pf = tk.Frame(tab, bg=COLORES["blanco"], width=300)
        pf.pack(side="left", fill="y", padx=20, pady=20)
        pf.pack_propagate(False)

        tk.Label(pf, text="Registrar Cliente",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", pady=(0, 15))

        self.entry_nombre   = self._campo(pf, "Nombre completo")
        self.entry_email    = self._campo(pf, "Correo electrónico")
        self.entry_telefono = self._campo(pf, "Teléfono")

        tk.Button(pf, text="+ Registrar Cliente",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORES["primario"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", pady=8,
                  command=self._registrar_cliente).pack(fill="x", pady=(15, 5))

        tk.Button(pf, text="🗑  Desactivar seleccionado",
                  font=("Segoe UI", 9),
                  bg=COLORES["error"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", pady=6,
                  command=self._desactivar_cliente).pack(fill="x")

        # Lista derecha
        pl = tk.Frame(tab, bg=COLORES["blanco"])
        pl.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        tk.Label(pl, text="Clientes registrados",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", pady=(0, 10))

        cols = ("ID", "Nombre", "Email", "Teléfono", "Estado")
        self.tree_clientes = self._tabla(pl, cols, [60, 150, 180, 100, 70])

    def _registrar_cliente(self):
        nombre   = self.entry_nombre.get().strip()
        email    = self.entry_email.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not nombre or not email or not telefono:
            messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
            return
        try:
            id_c = f"C{self._contador_clientes:03d}"
            c = Cliente(id_c, nombre, email, telefono)
            self.clientes.append(c)
            self._contador_clientes += 1
            self.tree_clientes.insert("", "end",
                values=(id_c, nombre, email, telefono, "Activo"))
            self.entry_nombre.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_telefono.delete(0, tk.END)
            self._actualizar_combos()
            messagebox.showinfo("✅ Éxito", f"Cliente '{nombre}' registrado.")
            self._refrescar_logs()
        except ErrorClienteInvalido as e:
            messagebox.showerror("❌ Error", str(e))

    def _desactivar_cliente(self):
        sel = self.tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un cliente.")
            return
        item = self.tree_clientes.item(sel[0])
        id_c = item["values"][0]
        for c in self.clientes:
            if c.id_entidad == id_c:
                if not c.activo:
                    messagebox.showinfo("Info", "El cliente ya está inactivo.")
                    return
                c.desactivar()
                vals = list(item["values"])
                vals[4] = "Inactivo"
                self.tree_clientes.item(sel[0], values=vals)
                self._actualizar_combos()
                messagebox.showinfo("✅ Listo", f"Cliente {id_c} desactivado.")
                self._refrescar_logs()
                return

    # ── TAB SERVICIOS ─────────────────────────────────────────────

    def _construir_tab_servicios(self):
        tab = self.tab_servicios

        tk.Label(tab, text="Servicios disponibles en Software FJ",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(tab, text="Los servicios están precargados en el sistema.",
                 font=("Segoe UI", 9), bg=COLORES["blanco"],
                 fg=COLORES["gris"]).pack(anchor="w", padx=20, pady=(0, 10))

        frame = tk.Frame(tab, bg=COLORES["blanco"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols = ("ID", "Nombre", "Precio/h", "Estado", "Detalle")
        self.tree_servicios = self._tabla(frame, cols, [60, 200, 90, 90, 250])

        for s in self.servicios:
            partes = s.describir().split(" | ")
            while len(partes) < 5:
                partes.append("")
            self.tree_servicios.insert("", "end", values=tuple(partes[:5]))

    # ── TAB RESERVAS ──────────────────────────────────────────────

    def _construir_tab_reservas(self):
        tab = self.tab_reservas

        # Formulario izquierdo
        pf = tk.Frame(tab, bg=COLORES["blanco"], width=320)
        pf.pack(side="left", fill="y", padx=20, pady=20)
        pf.pack_propagate(False)

        tk.Label(pf, text="Nueva Reserva",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", pady=(0, 15))

        tk.Label(pf, text="Cliente", font=("Segoe UI", 9),
                 bg=COLORES["blanco"], fg=COLORES["gris"]).pack(anchor="w")
        self.combo_clientes = ttk.Combobox(pf, state="readonly", font=("Segoe UI", 9))
        self.combo_clientes.pack(fill="x", pady=(2, 10))

        tk.Label(pf, text="Servicio", font=("Segoe UI", 9),
                 bg=COLORES["blanco"], fg=COLORES["gris"]).pack(anchor="w")
        self.combo_servicios = ttk.Combobox(pf, state="readonly", font=("Segoe UI", 9))
        self.combo_servicios["values"] = [s.nombre for s in self.servicios]
        self.combo_servicios.pack(fill="x", pady=(2, 10))

        self.entry_duracion = self._campo(pf, "Duración (horas)")

        tk.Label(pf, text="Opciones de pago",
                 font=("Segoe UI", 9, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", pady=(10, 5))

        self.var_impuesto = tk.BooleanVar()
        tk.Checkbutton(pf, text="Aplicar IVA (19%)",
                        variable=self.var_impuesto,
                        bg=COLORES["blanco"], font=("Segoe UI", 9)).pack(anchor="w")

        self.entry_descuento = self._campo(pf, "Descuento (0.0 – 1.0)")
        self.entry_monto     = self._campo(pf, "Monto a pagar ($)")

        btn_cfg = dict(font=("Segoe UI", 9), fg=COLORES["blanco"],
                       relief="flat", cursor="hand2", pady=6)

        tk.Button(pf, text="+ Crear Reserva",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORES["primario"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", pady=8,
                  command=self._crear_reserva).pack(fill="x", pady=(15, 5))

        tk.Button(pf, text="✅  Confirmar seleccionada",
                  bg=COLORES["exito"], command=self._confirmar_reserva,
                  **btn_cfg).pack(fill="x", pady=3)

        tk.Button(pf, text="💰  Procesar pago",
                  bg="#f29900", command=self._procesar_pago,
                  **btn_cfg).pack(fill="x", pady=3)

        tk.Button(pf, text="❌  Cancelar seleccionada",
                  bg=COLORES["error"], command=self._cancelar_reserva,
                  **btn_cfg).pack(fill="x", pady=3)

        # Lista derecha
        pl = tk.Frame(tab, bg=COLORES["blanco"])
        pl.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        tk.Label(pl, text="Reservas del sistema",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(anchor="w", pady=(0, 10))

        cols = ("ID", "Cliente", "Servicio", "Horas", "Estado", "Costo", "Fecha")
        self.tree_reservas = self._tabla(pl, cols, [60, 110, 140, 50, 80, 85, 120])
        self._actualizar_combos()

    def _crear_reserva(self):
        idx_c = self.combo_clientes.current()
        idx_s = self.combo_servicios.current()
        dur_str = self.entry_duracion.get().strip()

        if idx_c < 0 or idx_s < 0 or not dur_str:
            messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
            return
        try:
            duracion = float(dur_str)
            activos  = [c for c in self.clientes if c.activo]
            cliente  = activos[idx_c]
            servicio = self.servicios[idx_s]
            id_r     = f"R{self._contador_reservas:03d}"

            r = Reserva(id_r, cliente, servicio, duracion)
            self.reservas.append(r)
            self._contador_reservas += 1

            self.tree_reservas.insert("", "end", values=(
                id_r, cliente.nombre, servicio.nombre,
                duracion, "pendiente", f"${r._costo_total:,.0f}", r._fecha))

            self.entry_duracion.delete(0, tk.END)
            messagebox.showinfo("✅ Reserva creada", f"Reserva {id_r} creada exitosamente.")
            self._refrescar_logs()

        except (ErrorReservaInvalida, ErrorDuracionInvalida,
                ErrorServicioNoDisponible, ValueError) as e:
            messagebox.showerror("❌ Error", str(e))

    def _confirmar_reserva(self):
        sel = self.tree_reservas.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una reserva.")
            return
        id_r = self.tree_reservas.item(sel[0])["values"][0]
        try:
            r = next(x for x in self.reservas if x.id_reserva == id_r)
            r.confirmar()
            vals = list(self.tree_reservas.item(sel[0])["values"])
            vals[4] = "confirmada"
            self.tree_reservas.item(sel[0], values=vals)
            messagebox.showinfo("✅ Confirmada", f"Reserva {id_r} confirmada.")
            self._refrescar_logs()
        except ErrorReservaInvalida as e:
            messagebox.showerror("❌ Error", str(e))

    def _procesar_pago(self):
        sel = self.tree_reservas.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una reserva confirmada.")
            return
        id_r      = self.tree_reservas.item(sel[0])["values"][0]
        monto_str = self.entry_monto.get().strip()
        desc_str  = self.entry_descuento.get().strip() or "0"

        if not monto_str:
            messagebox.showwarning("Monto requerido", "Ingresa el monto a pagar.")
            return
        try:
            monto    = float(monto_str)
            descuento = float(desc_str)
            impuesto  = self.var_impuesto.get()
            r = next(x for x in self.reservas if x.id_reserva == id_r)
            cambio, costo = r.procesar_pago(monto, impuesto, descuento)

            vals = list(self.tree_reservas.item(sel[0])["values"])
            vals[4] = "completada"
            vals[5] = f"${costo:,.0f}"
            self.tree_reservas.item(sel[0], values=vals)

            messagebox.showinfo("💰 Pago exitoso",
                f"Pago procesado correctamente.\n"
                f"Costo final: ${costo:,.0f}\nCambio: ${cambio:,.0f}")
            self._refrescar_logs()

        except (ErrorReservaInvalida, ValueError) as e:
            messagebox.showerror("❌ Error en pago", str(e))

    def _cancelar_reserva(self):
        sel = self.tree_reservas.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una reserva.")
            return
        id_r = self.tree_reservas.item(sel[0])["values"][0]
        try:
            r = next(x for x in self.reservas if x.id_reserva == id_r)
            r.cancelar()
            vals = list(self.tree_reservas.item(sel[0])["values"])
            vals[4] = "cancelada"
            self.tree_reservas.item(sel[0], values=vals)
            messagebox.showinfo("❌ Cancelada", f"Reserva {id_r} cancelada.")
            self._refrescar_logs()
        except ErrorReservaInvalida as e:
            messagebox.showerror("❌ Error", str(e))

    # ── TAB SIMULACIÓN ────────────────────────────────────────────

    def _construir_tab_simulacion(self):
        tab = self.tab_simulacion

        top = tk.Frame(tab, bg=COLORES["blanco"])
        top.pack(fill="x", padx=20, pady=(20, 5))

        tk.Label(top, text="Simulación de operaciones del sistema",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(side="left")

        tk.Button(top, text="▶  Ejecutar simulación",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORES["exito"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", padx=14, pady=6,
                  command=self._ejecutar_simulacion).pack(side="right")

        tk.Label(tab,
                 text="Ejecuta automáticamente 12 operaciones: clientes, servicios, "
                      "reservas, pagos y cancelaciones (casos válidos e inválidos).",
                 font=("Segoe UI", 9), bg=COLORES["blanco"], fg=COLORES["gris"],
                 wraplength=860, justify="left").pack(anchor="w", padx=20, pady=(0, 10))

        frame = tk.Frame(tab, bg=COLORES["blanco"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.text_sim = tk.Text(frame, font=("Consolas", 9),
                                bg="#1e1e1e", fg="#d4d4d4",
                                relief="flat", wrap="word", state="disabled")
        sb = ttk.Scrollbar(frame, command=self.text_sim.yview)
        self.text_sim.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.text_sim.pack(fill="both", expand=True)

        # Colores de etiquetas para el widget Text
        self.text_sim.tag_configure("ok",    foreground="#4ec9b0")
        self.text_sim.tag_configure("error", foreground="#f44747")
        self.text_sim.tag_configure("titulo",foreground="#569cd6", font=("Consolas", 9, "bold"))
        self.text_sim.tag_configure("sep",   foreground="#555555")

    def _ejecutar_simulacion(self):
        """Ejecuta 12 operaciones de simulación cubriendo casos válidos e inválidos."""

        def escribir(linea, tag=""):
            self.text_sim.configure(state="normal")
            self.text_sim.insert(tk.END, linea + "\n", tag)
            self.text_sim.configure(state="disabled")
            self.text_sim.see(tk.END)

        def actualizar_fila_reserva(iid, reserva):
            """Sincroniza el estado y costo de una fila del tree_reservas."""
            vals = list(self.tree_reservas.item(iid)["values"])
            vals[4] = reserva.estado
            vals[5] = f"${reserva._costo_total:,.0f}"
            self.tree_reservas.item(iid, values=vals)

        # ── Limpiar área de texto ──────────────────────────────────
        self.text_sim.configure(state="normal")
        self.text_sim.delete("1.0", tk.END)
        self.text_sim.configure(state="disabled")

        # ── Limpiar tablas de entradas de simulaciones anteriores ──
        for item in self.tree_clientes.get_children():
            if str(self.tree_clientes.item(item)["values"][0]).startswith("C9"):
                self.tree_clientes.delete(item)
        self.clientes = [c for c in self.clientes if not c.id_entidad.startswith("C9")]

        for item in self.tree_reservas.get_children():
            if str(self.tree_reservas.item(item)["values"][0]).startswith("R9"):
                self.tree_reservas.delete(item)
        self.reservas = [r for r in self.reservas if not r.id_reserva.startswith("R9")]

        self._actualizar_combos()

        escribir("=" * 70, "sep")
        escribir("  SIMULACIÓN — Software FJ  |  12 operaciones", "titulo")
        escribir("=" * 70, "sep")

        clientes_sim = []
        reservas_sim = []
        iids_reservas = {}   # id_reserva → iid del treeview
        cont_r = 900

        # ── OP 1: Cliente válido ───────────────────────────────────
        escribir("\n[OP 1] Registrar cliente válido: Ana García", "titulo")
        try:
            c1 = Cliente("C901", "Ana García", "ana.garcia@gmail.com", "3001234567")
            clientes_sim.append(c1)
            self.clientes.append(c1)
            self.tree_clientes.insert("", "end",
                values=("C901", "Ana García", "ana.garcia@gmail.com", "3001234567", "Activo"))
            escribir(f"  ✔ Cliente creado: {c1.describir()}", "ok")
        except Exception as e:
            escribir(f"  ✘ Error inesperado: {e}", "error")

        # ── OP 2: Cliente válido ───────────────────────────────────
        escribir("\n[OP 2] Registrar cliente válido: Carlos López", "titulo")
        try:
            c2 = Cliente("C902", "Carlos López", "carlos@empresa.co", "3109876543")
            clientes_sim.append(c2)
            self.clientes.append(c2)
            self.tree_clientes.insert("", "end",
                values=("C902", "Carlos López", "carlos@empresa.co", "3109876543", "Activo"))
            escribir(f"  ✔ Cliente creado: {c2.describir()}", "ok")
        except Exception as e:
            escribir(f"  ✘ Error inesperado: {e}", "error")

        self._actualizar_combos()

        # ── OP 3: Cliente inválido — email sin @ ───────────────────
        escribir("\n[OP 3] Registrar cliente INVÁLIDO (email sin @)", "titulo")
        try:
            Cliente("C903", "Pedro Sin-Arroba", "correosinArroba.com", "3201111111")
            escribir("  ✘ Debió lanzar excepción", "error")
        except ErrorClienteInvalido as e:
            registrar_log("error", f"Simulación OP3: {e}")
            escribir(f"  ✔ Excepción capturada → ErrorClienteInvalido: {e}", "ok")

        # ── OP 4: Cliente inválido — teléfono muy corto ────────────
        escribir("\n[OP 4] Registrar cliente INVÁLIDO (teléfono 4 dígitos)", "titulo")
        try:
            Cliente("C904", "Laura Corta", "laura@ok.com", "1234")
            escribir("  ✘ Debió lanzar excepción", "error")
        except ErrorClienteInvalido as e:
            registrar_log("error", f"Simulación OP4: {e}")
            escribir(f"  ✔ Excepción capturada → ErrorClienteInvalido: {e}", "ok")

        # ── OP 5: Reserva de sala válida ───────────────────────────
        escribir("\n[OP 5] Crear reserva de sala válida (Ana, 3 horas)", "titulo")
        try:
            sala = self.servicios[0]
            id_r = f"R{cont_r}"; cont_r += 1
            r1 = Reserva(id_r, clientes_sim[0], sala, 3)
            reservas_sim.append(r1)
            self.reservas.append(r1)
            iid = self.tree_reservas.insert("", "end", values=(
                id_r, clientes_sim[0].nombre, sala.nombre,
                3, "pendiente", f"${r1._costo_total:,.0f}", r1._fecha))
            iids_reservas[id_r] = iid
            escribir(f"  ✔ Reserva creada: {r1.describir()}", "ok")
        except Exception as e:
            escribir(f"  ✘ Error: {e}", "error")

        # ── OP 6: Reserva de equipo válida ─────────────────────────
        escribir("\n[OP 6] Crear reserva de equipo válida (Carlos, 10 horas)", "titulo")
        try:
            equipo = self.servicios[2]
            id_r = f"R{cont_r}"; cont_r += 1
            r2 = Reserva(id_r, clientes_sim[1], equipo, 10)
            reservas_sim.append(r2)
            self.reservas.append(r2)
            iid = self.tree_reservas.insert("", "end", values=(
                id_r, clientes_sim[1].nombre, equipo.nombre,
                10, "pendiente", f"${r2._costo_total:,.0f}", r2._fecha))
            iids_reservas[id_r] = iid
            escribir(f"  ✔ Reserva creada: {r2.describir()}", "ok")
        except Exception as e:
            escribir(f"  ✘ Error: {e}", "error")

        # ── OP 7: Reserva de asesoría INVÁLIDA (duración > 8h) ─────
        escribir("\n[OP 7] Crear reserva de asesoría INVÁLIDA (15 horas > máx 8h)", "titulo")
        try:
            asesoria = self.servicios[4]
            Reserva(f"R{cont_r}", clientes_sim[0], asesoria, 15)
            escribir("  ✘ Debió lanzar excepción", "error")
        except ErrorDuracionInvalida as e:
            registrar_log("error", f"Simulación OP7: {e}")
            escribir(f"  ✔ Excepción capturada → ErrorDuracionInvalida: {e}", "ok")

        # ── OP 8: Confirmar reserva R900 ───────────────────────────
        escribir("\n[OP 8] Confirmar reserva R900 (sala)", "titulo")
        try:
            reservas_sim[0].confirmar()
            actualizar_fila_reserva(iids_reservas[reservas_sim[0].id_reserva], reservas_sim[0])
            escribir(f"  ✔ Estado: {reservas_sim[0].estado}", "ok")
        except ErrorReservaInvalida as e:
            escribir(f"  ✘ Error: {e}", "error")

        # ── OP 9: Pago exitoso R900 ────────────────────────────────
        escribir("\n[OP 9] Procesar pago exitoso en R900 (con IVA 19%, sin descuento)", "titulo")
        try:
            cambio, costo = reservas_sim[0].procesar_pago(
                monto_pagado=300000, aplicar_impuesto=True, descuento=0.0)
            iid = iids_reservas[reservas_sim[0].id_reserva]
            vals = list(self.tree_reservas.item(iid)["values"])
            vals[4] = "completada"
            vals[5] = f"${costo:,.0f}"
            self.tree_reservas.item(iid, values=vals)
            escribir(f"  ✔ Pago aceptado | Costo final: ${costo:,.0f} | Cambio: ${cambio:,.0f}", "ok")
        except ErrorReservaInvalida as e:
            escribir(f"  ✘ Error en pago: {e}", "error")

        # ── OP 10: Confirmar y pagar R901 con monto INSUFICIENTE ───
        escribir("\n[OP 10] Confirmar y pagar R901 con monto INSUFICIENTE", "titulo")
        try:
            reservas_sim[1].confirmar()
            actualizar_fila_reserva(iids_reservas[reservas_sim[1].id_reserva], reservas_sim[1])
            escribir(f"  ✔ R901 confirmada", "ok")
            reservas_sim[1].procesar_pago(monto_pagado=5000)
            escribir("  ✘ Debió lanzar excepción", "error")
        except ErrorReservaInvalida as e:
            registrar_log("error", f"Simulación OP10: {e}")
            escribir(f"  ✔ Excepción capturada → ErrorReservaInvalida: {e}", "ok")

        # ── OP 11: Cancelar reserva R901 ──────────────────────────
        escribir("\n[OP 11] Cancelar reserva R901", "titulo")
        try:
            reservas_sim[1].cancelar()
            actualizar_fila_reserva(iids_reservas[reservas_sim[1].id_reserva], reservas_sim[1])
            escribir(f"  ✔ Estado: {reservas_sim[1].estado}", "ok")
        except ErrorReservaInvalida as e:
            escribir(f"  ✘ Error: {e}", "error")

        # ── OP 12: Intentar cancelar reserva YA COMPLETADA ────────
        escribir("\n[OP 12] Cancelar reserva R900 (ya está COMPLETADA — debe fallar)", "titulo")
        try:
            reservas_sim[0].cancelar()
            escribir("  ✘ Debió lanzar excepción", "error")
        except ErrorReservaInvalida as e:
            registrar_log("error", f"Simulación OP12: {e}")
            escribir(f"  ✔ Excepción capturada → ErrorReservaInvalida: {e}", "ok")

        escribir("\n" + "=" * 70, "sep")
        escribir("  Simulación completada. Revisa las pestañas 👤 Clientes y 📅 Reservas.", "titulo")
        escribir("=" * 70, "sep")

        registrar_log("info", "Simulación de 12 operaciones ejecutada correctamente.")
        self._refrescar_logs()

    # ── TAB LOGS ──────────────────────────────────────────────────

    def _construir_tab_logs(self):
        tab = self.tab_logs

        top = tk.Frame(tab, bg=COLORES["blanco"])
        top.pack(fill="x", padx=20, pady=(20, 5))
        tk.Label(top, text="Registro de eventos del sistema",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORES["blanco"], fg=COLORES["texto"]).pack(side="left")
        tk.Button(top, text="🔄 Actualizar",
                  font=("Segoe UI", 9),
                  bg=COLORES["primario"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", padx=10,
                  command=self._refrescar_logs).pack(side="right")

        frame = tk.Frame(tab, bg=COLORES["blanco"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.text_logs = tk.Text(frame, font=("Consolas", 9),
                                  bg="#1e1e1e", fg="#d4d4d4",
                                  relief="flat", wrap="word", state="disabled")
        sb = ttk.Scrollbar(frame, command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.text_logs.pack(fill="both", expand=True)
        self._refrescar_logs()

    def _refrescar_logs(self):
        """Lee el archivo de logs y lo muestra en pantalla."""
        self.text_logs.configure(state="normal")
        self.text_logs.delete("1.0", tk.END)
        try:
            with open("software_fj_logs.txt", "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read()
            self.text_logs.insert(tk.END, contenido or "Sin eventos registrados aún.")
        except FileNotFoundError:
            self.text_logs.insert(tk.END, "Archivo de logs no encontrado aún.")
        self.text_logs.configure(state="disabled")
        self.text_logs.see(tk.END)

    # ── UTILIDADES ────────────────────────────────────────────────

    def _campo(self, parent, placeholder):
        """Crea un campo de entrada con etiqueta."""
        tk.Label(parent, text=placeholder, font=("Segoe UI", 9),
                 bg=COLORES["blanco"], fg=COLORES["gris"]).pack(anchor="w")
        e = tk.Entry(parent, font=("Segoe UI", 10),
                     relief="solid", bd=1,
                     highlightthickness=1,
                     highlightcolor=COLORES["primario"])
        e.pack(fill="x", pady=(2, 10), ipady=5)
        return e

    def _tabla(self, parent, columnas, anchos):
        """Crea una tabla Treeview con scrollbar vertical."""
        style = ttk.Style()
        style.configure("Treeview",
                         font=("Segoe UI", 9), rowheight=28,
                         background=COLORES["blanco"],
                         fieldbackground=COLORES["blanco"])
        style.configure("Treeview.Heading",
                         font=("Segoe UI", 9, "bold"),
                         background=COLORES["secundario"],
                         foreground=COLORES["texto"])

        frame = tk.Frame(parent, bg=COLORES["blanco"])
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=columnas,
                             show="headings", selectmode="browse")
        for col, ancho in zip(columnas, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

    def _actualizar_combos(self):
        """Actualiza el combo de clientes activos en la pestaña de reservas."""
        activos = [c.nombre for c in self.clientes if c.activo]
        self.combo_clientes["values"] = activos
        if activos:
            self.combo_clientes.current(0)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaFJ(root)
    root.mainloop()
