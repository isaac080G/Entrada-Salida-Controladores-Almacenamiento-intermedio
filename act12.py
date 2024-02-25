# Hernandez Chavez Isaac Alberto
# 215769734
# seminario de solucion de sistemas operativos
import tkinter as tk
import time
import threading
import random
from tkinter import ttk
import queue
import math
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import messagebox
import keyboard
import pyautogui

NUMERO_DE_RECUADROS_REAL = 25
NUMERO_DE_RECUADROS_VIRTUAL = 25
TOTAL_DE_RECUADROS = NUMERO_DE_RECUADROS_REAL+NUMERO_DE_RECUADROS_VIRTUAL

# se declara la lista de caracter global
lista_de_procesos = []
# aqui estan los recuadros de la simulacion de memoria
cuadros = {}
# lista de recuadros usados
espacios_disponibles = []
# valores necesarios para las progressbar
valor_real = 0
valor_virtual = 0

# configuracion de ventana
ventana = tk.Tk()
ventana.title("Hernandez chavez isaac alberto")
ventana.geometry("1460x650")
# ventana.configure(bg="#C300C9")
ventana.configure(relief="ridge")

# Variables globales para pausar y detener los procesos
pausar_proceso_A = threading.Event()
pausar_proceso_B = threading.Event()
pausar_proceso_C = threading.Event()
pausar_proceso_D = threading.Event()

detener_proceso = threading.Event()

# aux letras
letras_mayusculas = [chr(i) for i in range(ord('A'), ord('Z')+1)]
letras_minusculas = [chr(i) for i in range(ord('a'), ord('z')+1)]
numeros = [str(i) for i in range(0, 10)]
caracteres_especiales = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':',
                         ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ' ', '\t', '\n']
# semaforos
# ESTA PARTE ES DE SUMA IMPORTANCIA PARA  QUE NO SE EJECUTEN MAS DE DOS HILOS A LA VEZ, ESTA LIMITADO A UN PROCESO A LA VEZ
semaphore_general = threading.Semaphore(1)
# en prioridad fue necesario el agregar un segundo semaforo
semaphore_general_2 = threading.Semaphore(1)

# semaforo necesario para la actualizacion de 17/11/2023
semaphore_general_A = threading.Semaphore(1)


# error memoria llena
def mostrar_alerta_de_error():
    messagebox.showerror("Error", "memoria llena")


# listas particulares
listas_individuales = {"A": [],
                       "B": [],
                       "C": [],
                       "D": []}

ubicaciones = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4}
contador = 1


# barras de progreso la declaracion de donde van esta en la funcoin para memoria
progress_bar_real = ttk.Progressbar(
    ventana, orient="horizontal", length=250, mode="determinate", style="TProgressbar")
progress_bar_virtual = ttk.Progressbar(
    ventana, orient="horizontal", length=250, mode="determinate", style="TProgressbar")

# funcion encargada de "liberar" espacios en la cuadricula


def decolorar(nombre):
    global valor_virtual
    global valor_real
    terminado = tk.Label(ventana, text="concluido",
                         font=("Arial", 9, "bold"), fg="red")
    terminado.grid(row=ubicaciones[nombre], column=10)

    for cuadro in listas_individuales[nombre]:
        direccion = "0x7FFFD"+str(cuadro)
        valor = cuadros[cuadro]
        valor.create_rectangle(0, 0, 50, 50, fill="white",
                               outline="blue", width=2)
        valor.create_text(25, 25, text=direccion,
                          fill="black", font=("arial", 6))
        if cuadro < NUMERO_DE_RECUADROS_REAL:
            valor_real -= (100/NUMERO_DE_RECUADROS_REAL)
            progress_bar_real.config(value=valor_real)
        else:
            valor_virtual -= (100/NUMERO_DE_RECUADROS_VIRTUAL)
            progress_bar_virtual.config(value=valor_virtual)
        time.sleep(0.1)


# procesos
style = ttk.Style()


class proceso_objet:
    def __init__(self, nombre, hilo, prioridad, tamano) -> None:
        self.nombre = nombre
        # self.tiempo=tiempo en esta atividad prescindimos del atributo tiempo
        self.priority = prioridad  # en esta actividad tenemos el uso del temino prioridad
        self.hilo = hilo
        self.tamano = tamano  # creado para la actividad 09

# en esta funcion se hace el decremento de la progress bar


def kill_proceso(progress_bar, nombre):
    valor = 100

    while valor > 0:
        # cambiar_color_estilo(valor)
        ventana.after(100, lambda p=progress_bar,
                      v=valor: p.configure(value=v))
        valor -= 1
        ventana.update_idletasks()
        time.sleep(0.1)
    if valor == 0:
        valor -= 1
        print("aqui estoy")  # control
        ventana.after(100, lambda p=progress_bar,
                      v=valor: p.configure(value=v))
        ventana.update_idletasks()
        decolorar(nombre)

# detecion de dispositivos


def dispositivos(dispositivo):
    if dispositivo == "teclado":
        label_de_deteccion = tk.Label(
            ventana, text="Teclado detectado", fg="green", font=("Arial", 10))
        label_de_deteccion.grid(row=16, column=20, columnspan=3)
        time.sleep(0.1)
        label_de_deteccion.destroy()
    # elif dispositivo ==mouse futura actualizacion
        x, y = pyautogui.position()
        coodenadas = "x="+str(x)+" y="+str(y)
        label_de_deteccion_mouse_aux = tk.Label(
            ventana, text=coodenadas, font=("arial", 8))
        label_de_deteccion_mouse_aux.grid(row=17, column=22, columnspan=3)
# Función para iniciar el proceso de actualización de la barra de progreso
# en esta seccion del codigo se detienen cada una de las secciones del mismo (barras de progreso)


def actualizar_barra_de_progreso(progress_bar, nombre_proceso, tamano):
    # ESTA PARTE ES DE SUMA IMPORTANCIA PARA  QUE NO SE EJECUTEN MAS DE DOS HILOS A LA VEZ

    valor = 0
    # labels
    label_A = tk.Label(ventana, text='A', fg="green")
    label_B = tk.Label(ventana, text='B', fg="green")
    label_C = tk.Label(ventana, text='C', fg="green")
    label_D = tk.Label(ventana, text='D', fg="green")
    # LABELS TERMINADO
    label_A_terminado = tk.Label(ventana, text='A', fg="red")
    label_B_terminado = tk.Label(ventana, text='B', fg="red")
    label_C_terminado = tk.Label(ventana, text='C', fg="red")
    label_D_terminado = tk.Label(ventana, text='D', fg="red")

    while valor < 100:  # proceso A
        if nombre_proceso == "A":
            for letra in letras_mayusculas:
                if not pausar_proceso_A.is_set() and keyboard.is_pressed(letra):
                    # label de deteccion
                    dispositivos("teclado")
                    valor += random.uniform(1, 3)
                    if valor < 100:
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=v))
                        ventana.update_idletasks()
                        # ceracion de tabla
                        label_A.grid(row=8, column=2)
                        labelCola_A.grid_forget()

                    else:
                        # destruccion de label
                        label_A.grid_forget()
                        label_A.destroy()
                        # NUEVO LABEL
                        label_A_terminado.grid(row=11, column=2)
                        print("si entra")
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=100))
                        # en esta parte del codigo se hace uso de la funcion kill , para "consumir" el proceso
                        kill = threading.Thread(
                            target=kill_proceso, args=(progress_bar, nombre_proceso))
                        # label de consumir
                        consumiendo = tk.Label(ventana, text="Guardando", font=(
                            "Arial", 9, "bold"), fg="red")
                        consumiendo.grid(row=1, column=10)
                        kill.start()
                        colorear_hilo = threading.Thread(
                            target=para_la_memoria, args=(tamano, nombre_proceso))
                        colorear_hilo.start()
                        ventana.update_idletasks()
            ventana.update()

        if nombre_proceso == "B":  # proceso B
            for letra_B in letras_minusculas:

                if not pausar_proceso_B.is_set() and keyboard.is_pressed(letra_B):
                    dispositivos("teclado")
                    valor += random.uniform(1, 10)
                    if valor <= 100:
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=v))
                        ventana.update_idletasks()

                        label_B.grid(row=8, column=3)
                        labelCola_B.grid_forget()

                    if valor > 100:
                        # destruccion de label
                        label_B.grid_forget()
                        label_B.destroy()
                        # en esta parte del codigo se hace uso de la funcion kill , para "consumir" el proceso
                        kill = threading.Thread(
                            target=kill_proceso, args=(progress_bar, nombre_proceso))
                        kill.start()
                        # NUEVO LABEL
                        label_B_terminado.grid(row=11, column=3)
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=100))
                        # label de consumir
                        consumiendo = tk.Label(ventana, text="Guardando", font=(
                            "Arial", 9, "bold"), fg="red")
                        consumiendo.grid(row=2, column=10)
                        colorear_hilo = threading.Thread(
                            target=para_la_memoria, args=(tamano, nombre_proceso))
                        colorear_hilo.start()
                        ventana.update_idletasks()

        if nombre_proceso == "C":  # proceso C
            for letra in numeros:

                if not pausar_proceso_C.is_set() and keyboard.is_pressed(letra):
                    dispositivos("teclado")

                    valor += random.uniform(1, 7)
                    if valor <= 100:
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=v))
                        ventana.update_idletasks()

                        label_C.grid(row=8, column=5)
                        labelCola_C.grid_forget()

                    if valor > 100:
                        # destruccion de label
                        label_C.grid_forget()
                        label_C.destroy()
                        # en esta parte del codigo se hace uso de la funcion kill , para "consumir" el proceso
                        kill = threading.Thread(
                            target=kill_proceso, args=(progress_bar, nombre_proceso))
                        kill.start()
                        # NUEVO LABEL
                        label_C_terminado.grid(row=11, column=5)
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=100))
                        # label de consumir
                        consumiendo = tk.Label(ventana, text="Guardando", font=(
                            "Arial", 9, "bold"), fg="red")
                        consumiendo.grid(row=3, column=10)
                        colorear_hilo = threading.Thread(
                            target=para_la_memoria, args=(tamano, nombre_proceso))
                        colorear_hilo.start()
                        ventana.update_idletasks()

        if nombre_proceso == "D":  # proceso D
            for letra in caracteres_especiales:
                if not pausar_proceso_D.is_set() and keyboard.is_pressed(letra):
                    dispositivos("teclado")

                    valor += random.uniform(1, 3)
                    if valor <= 100:
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=v))
                        ventana.update_idletasks()

                        label_D.grid(row=8, column=7)
                        labelCola_D.grid_forget()

                    if valor > 100:
                        # destruccion de label
                        label_D.grid_forget()
                        label_D.destroy()
                        # en esta parte del codigo se hace uso de la funcion kill , para "consumir" el proceso
                        kill = threading.Thread(
                            target=kill_proceso, args=(progress_bar, nombre_proceso))
                        kill.start()
                        # NUEVO LABEL
                        label_D_terminado.grid(row=11, column=7)
                        ventana.after(100, lambda p=progress_bar,
                                      v=valor: p.configure(value=100))
                        # label de consumir
                        consumiendo = tk.Label(ventana, text="Guardando", font=(
                            "Arial", 9, "bold"), fg="red")
                        consumiendo.grid(row=4, column=10)
                        colorear_hilo = threading.Thread(
                            target=para_la_memoria, args=(tamano, nombre_proceso))
                        colorear_hilo.start()
                        ventana.update_idletasks()

        time.sleep(0.1)

        if detener_proceso.is_set():
            progress_bar.configure(value=0)
            break

    semaphore_general.release()
# Función que representa una fase de ejecución de un proceso


def fase_ejecucion(nombre_proceso, progress_bar):
    print(
        f"Fase de Ejecución del Proceso {nombre_proceso}: El proceso se está ejecutando")


# Función que inicia un proceso
def iniciar_proceso(nombre_proceso, progress_bar, tamano):
    semaphore_general_2.acquire()
    progress_bar.start()
    t_actualizacion_1 = threading.Thread(
        target=actualizar_barra_de_progreso, args=(progress_bar, nombre_proceso, tamano))
    t_ejecucion = threading.Thread(
        target=fase_ejecucion, args=(nombre_proceso, progress_bar))

    t_actualizacion_1.start()
    # t_actualizacion_2.start()
    # t_actualizacion_3.start()
    # t_actualizacion_4.start()
    t_ejecucion.start()
    t_ejecucion.join()

    progress_bar.stop()
    semaphore_general_2.release()


# Crear una barra de progreso determinada para cada proceso
progress_bars = []
style.configure("TProgressbar", troughcolor="gray", barcolor="green")

# lables necesarios para la version hecha el 17/11/2023
letrero = ["Mayusculas", "Minusculas", "Numeros", "Especiales"]
aux_letrero = 0
# aqui se crean las progress bar
for i, proceso in enumerate(["A", "B", "C", "D"]):

    progress_bar = ttk.Progressbar(
        ventana, orient="horizontal", length=200, mode="determinate", style="TProgressbar")
    progress_bar.grid(row=i+1, column=1, columnspan=3, padx=10, pady=10)
    letra = tk.Label(ventana, text=letrero[aux_letrero])
    aux_letrero += 1
    letra.grid(row=i+1, column=0)
    progress_bars.append(progress_bar)

# labels***********************************************************************
enTerminacion = tk.Label(ventana, text="terminado:", font=("Arial", 9, "bold"))
enTerminacion.grid(row=11, column=0, rowspan=2)

enEjecucion = tk.Label(ventana, text="ejecutandose:",
                       font=("Arial", 9, "bold"))
enEjecucion.grid(row=8, column=0, rowspan=2)

# prioridad label
prioridad = tk.Label(ventana, text="tamaño:", font=("Arial", 9, "bold"))
prioridad.grid(row=13, column=0, rowspan=2)

# labels esteticos
linea = tk.Label(
    ventana, text="--------------------------------------------------------------------------------------------------------", font=("Arial", 9, "bold"))
linea.grid(row=11, column=1, columnspan=8)

linea2 = tk.Label(
    ventana, text="-------------------------------------------------------------------------------------------------------", font=("Arial", 9, "bold"))
linea2.grid(row=8, column=1, columnspan=8)

linea3 = tk.Label(
    ventana, text="-------------------------------------------------------------------------------------------------------", font=("Arial", 9, "bold"))
linea3.grid(row=7, column=1, columnspan=8)


# label de cola****************************************************************
labelCola = tk.Label(ventana, text=" En cola:", font=("Arial", 9, "bold"))
labelCola.grid(row=7, column=0)
# labels de cola****************************************************************
labelCola_A = tk.Label(ventana, text="A")
labelCola_A.grid(row=7, column=2)
labelCola_B = tk.Label(ventana, text="B")
labelCola_B.grid(row=7, column=3)
labelCola_C = tk.Label(ventana, text="C")
labelCola_C.grid(row=7, column=5)
labelCola_D = tk.Label(ventana, text="D")
labelCola_D.grid(row=7, column=7)

# Botón para pausar A
boton_pausarA = tk.Button(ventana, text="Pausar/Reanudar", command=lambda: pausar_proceso_A.set()
                          if not pausar_proceso_A.is_set() else pausar_proceso_A.clear())
boton_pausarA.grid(row=1, column=6, columnspan=3, padx=10, pady=10)
# Botón para pausar B
boton_pausarB = tk.Button(ventana, text="Pausar/Reanudar", command=lambda: pausar_proceso_B.set()
                          if not pausar_proceso_B.is_set() else pausar_proceso_B.clear())
boton_pausarB.grid(row=2, column=6, columnspan=3, padx=10, pady=10)
# Botón para pausar C
boton_pausarC = tk.Button(ventana, text="Pausar/Reanudar", command=lambda: pausar_proceso_C.set()
                          if not pausar_proceso_C.is_set() else pausar_proceso_C.clear())
boton_pausarC.grid(row=3, column=6, columnspan=3, padx=10, pady=10)
# Botón para pausar D
boton_pausarD = tk.Button(ventana, text="Pausar/Reanudar", command=lambda: pausar_proceso_D.set()
                          if not pausar_proceso_D.is_set() else pausar_proceso_D.clear())
boton_pausarD.grid(row=4, column=6, columnspan=3, padx=10, pady=10)


# pausa de procesos


def pausa_general():
    boton_pausarA.invoke()
    boton_pausarB.invoke()
    boton_pausarC.invoke()
    boton_pausarD.invoke()

# ---------------------------------funcion para la memoria


def generar_cuadro():
    location_x = 13
    location_y = 1
    location_x_virtual = location_x+7

    contador_aux = 0
    for i in range(NUMERO_DE_RECUADROS_REAL):  # aqui se gener el cuadro de memoria real
        canvas = tk.Canvas(ventana, width=50, height=50)
        canvas.create_rectangle(0, 0, 50, 50, outline="black", width=2)
        direccion = "0x7FFFD"+str(contador_aux)
        canvas.create_text(25, 25, text=direccion,
                           fill="black", font=("arial", 6))
        canvas.grid(row=location_y, column=location_x)
        if location_x > 16:
            location_x = 13
            location_y += 1
        else:
            location_x += 1
        contador_aux += 1
        cuadros[i] = canvas

    location_y = 1

    # aqui se gener el cuadro de memoria virtual
    for i in range(NUMERO_DE_RECUADROS_REAL, (NUMERO_DE_RECUADROS_VIRTUAL+NUMERO_DE_RECUADROS_REAL)):
        canvas = tk.Canvas(ventana, width=50, height=50)
        canvas.create_rectangle(0, 0, 50, 50, outline="black", width=2)
        direccion = "0x7FFFD"+str(contador_aux)
        canvas.create_text(25, 25, text=direccion,
                           fill="black", font=("arial", 6))
        canvas.grid(row=location_y, column=location_x_virtual)
        if location_x_virtual > 23:
            location_x_virtual = location_x+7
            location_y += 1
        else:
            location_x_virtual += 1
        contador_aux += 1
        cuadros[i] = canvas

    # ya no me gusto canvas_muestra.create_rectangle(0, 0, 60, 60, fill="white", outline="black", width=2)

    texto_de_muestra = tk.Label(
        ventana, text=" Cada recuadro equivale a 50 MB")
    texto_de_muestra.grid(row=(location_y+5), column=12+1,
                          columnspan=NUMERO_DE_RECUADROS_REAL)

    # label de real y virtual
    label_real = tk.Label(ventana, text="Disco D:", font=("arial", 12))
    label_virtual = tk.Label(ventana, text="Disco C:", font=("arial", 12))
    label_real.grid(row=location_y+2, column=15)
    label_virtual.grid(row=location_y+2, column=22)

    estilo = ttk.Style()
    estilo.configure("TProgressbar", thickness=10)
    # barras de estado en las memorias

    progress_bar_real.grid(row=(location_y+3), column=13,
                           columnspan=5, padx=10, pady=10)
    progress_bar_virtual.grid(
        row=(location_y+3), column=20, columnspan=5, padx=10, pady=10)


generar_cuadro()


def para_la_memoria(tamano, nombre):
    global valor_real
    global valor_virtual

    semaphore_general_2.acquire()
    time.sleep(0.1)
    if len(espacios_disponibles) > 3:
        espacios_ocupados = []
        n_recuadros = math.ceil(tamano/50)
        while n_recuadros > len(espacios_disponibles):
            if nombre == "A":
                pausar_proceso_A.set()
            elif nombre == "B":
                pausar_proceso_B.set()
            elif nombre == "C":
                pausar_proceso_C.set()
            elif nombre == "D":
                pausar_proceso_D.set()

        # semaphore_general.acquire()
        if nombre == "A":
            for i in range(n_recuadros):  # colorear
                time.sleep(0.1)
                a_colorear = espacios_disponibles.pop(0)
                espacios_ocupados.append(a_colorear)
                valor = cuadros[a_colorear]
                valor.create_rectangle(
                    0, 0, 50, 50, fill="red", outline="blue", width=2)
                valor.create_text(25, 25, text=nombre,
                                  fill="black", font=("arial", 7))
                espacios_disponibles.extend(espacios_ocupados)
                if valor_real < 100:
                    valor_real += 100/NUMERO_DE_RECUADROS_REAL
                    progress_bar_real.config(
                        value=valor_real)
                else:
                    valor_virtual += 100/NUMERO_DE_RECUADROS_VIRTUAL
                    progress_bar_virtual.config(value=valor_virtual)
        elif nombre == "B":

            for i in range(n_recuadros):
                time.sleep(0.1)
                a_colorear = espacios_disponibles.pop(0)
                espacios_ocupados.append(a_colorear)
                valor = cuadros[a_colorear]
                valor.create_rectangle(
                    0, 0, 50, 50, fill="yellow", outline="blue", width=2)
                valor.create_text(25, 25, text=nombre,
                                  fill="black", font=("arial", 7))
                espacios_disponibles.extend(espacios_ocupados)
                if valor_real < 100:
                    valor_real += 100/NUMERO_DE_RECUADROS_REAL
                    progress_bar_real.config(
                        value=valor_real)
                else:
                    valor_virtual += 100/NUMERO_DE_RECUADROS_VIRTUAL
                    progress_bar_virtual.config(value=valor_virtual)
        elif nombre == "C":

            for i in range(n_recuadros):
                time.sleep(0.1)
                a_colorear = espacios_disponibles.pop(0)
                espacios_ocupados.append(a_colorear)
                valor = cuadros[a_colorear]
                valor.create_rectangle(
                    0, 0, 50, 50, fill="green", outline="blue", width=2)
                valor.create_text(25, 25, text=nombre,
                                  fill="black", font=("arial", 7))
                espacios_disponibles.extend(espacios_ocupados)
                if valor_real < 100:
                    valor_real += 100/NUMERO_DE_RECUADROS_REAL
                    progress_bar_real.config(
                        value=valor_real)
                else:
                    valor_virtual += 100/NUMERO_DE_RECUADROS_VIRTUAL
                    progress_bar_virtual.config(value=valor_virtual)
        elif nombre == "D":

            for i in range(n_recuadros):
                time.sleep(0.1)
                a_colorear = espacios_disponibles.pop(0)
                espacios_ocupados.append(a_colorear)
                valor = cuadros[a_colorear]
                valor.create_rectangle(
                    0, 0, 50, 50, fill="orange", outline="blue", width=2)
                valor.create_text(25, 25, text=nombre,
                                  fill="black", font=("arial", 7))
                espacios_disponibles.extend(espacios_ocupados)
                if valor_real < 100:
                    valor_real += 100/NUMERO_DE_RECUADROS_REAL
                    progress_bar_real.config(
                        value=valor_real)
                else:
                    valor_virtual += 100/NUMERO_DE_RECUADROS_VIRTUAL
                    progress_bar_virtual.config(value=valor_virtual)
        semaphore_general.release()
        listas_individuales[nombre] = espacios_ocupados[:]
        if valor_real >= 100 and valor_virtual > 100:
            pausa_general()
            mostrar_alerta_de_error()

    semaphore_general_2.release()

# en actividades anteriores se llama desencolar


def correr_lista():
    lista_objetos_ordenada = sorted(
        lista_de_procesos, key=lambda x: x.priority)
    aux = 1
    for proceso in lista_objetos_ordenada:

        print(proceso.nombre + "lista")
        proceso.hilo.start()

        # lista de prioridad
        text = proceso.nombre + " " + str(proceso.tamano)+"MB"
        prioridad_list = tk.Label(ventana, text=text)
        prioridad_list.grid(row=13, column=aux)
        aux += 1


##################################################################################
# cuadro de texto y dipositivos
cuadro_text = tk.Text(ventana, width=80, height=10)
cuadro_text.grid(row=15, column=2, columnspan=17, rowspan=7)

label_de_deteccion_todos = tk.Label(
    ventana, text="Dispositivos encontrados", font=("arial", 10))
label_de_deteccion_todos.grid(row=15, column=20, columnspan=3)

label_de_deteccion = tk.Label(
    ventana, text="Teclado detectado", fg="red", font=("arial", 10))
label_de_deteccion.grid(row=16, column=20, columnspan=3)

label_de_deteccion_mouse = tk.Label(
    ventana, text="raton", fg="green", font=("arial", 10))
label_de_deteccion_mouse.grid(row=17, column=20, columnspan=2)
###################################################################################

############################################ labels nuevos version 28/10/2023##################
estado = tk.Label(ventana, text="Estado", font=("Impact", 13))
estado.grid(row=0, column=10)

memoria = tk.Label(ventana, text="memorias", font=("Impact", 13))
memoria.grid(row=0, column=18)

proceso = tk.Label(ventana, text="proceso", font=("Impact", 13))
proceso.grid(row=0, column=0)


# recuadros decorativo
imagen_original = Image.open("ram(1).png")
tamano_X = 50
tamano_y = 50
imagen_redimensionada = imagen_original.resize((tamano_X, tamano_y))
imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
label_imagen = tk.Label(ventana, image=imagen_tk)
label_imagen_2 = tk.Label(ventana, image=imagen_tk)
label_imagen.grid(row=1, column=12)
label_imagen_2.grid(row=1, column=18)
# Recuadro de memoria


#################################################################################################

# se crea esta funcion para evitar hacer uso de demasiadas variables globales


def inicio():
    # Iniciar los procesos en hilos separados
    for i in range(TOTAL_DE_RECUADROS):
        espacios_disponibles.append(i)
    for i, proceso in enumerate(["A", "B", "C", "D"]):
        print(proceso)
        tamano_file = random.randint(250, 800)
        t_proceso = threading.Thread(
            target=iniciar_proceso, args=(proceso, progress_bars[i], tamano_file))

        newProceso = proceso_objet(
            proceso, t_proceso, random.randint(1, 3), tamano_file)  # aqui se modifica el tamaño de los procesos
        print(proceso, newProceso.priority)
        # tenemos tres tipos de prioridad
        # 1 muy imoportante  2' medianamente importante 3'poco importante
        lista_de_procesos.append(newProceso)

    # simplemente para hacer mas divertida la ejecucion del programa

    correr_lista()


inicio()
ventana.mainloop()
