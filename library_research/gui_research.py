
import tkinter as tk
from tkinter import messagebox

# Crear la ventana principal
root = tk.Tk()

# Establecer el título de la ventana
root.title("Ventana Simple con Tkinter")

# Establecer las dimensiones de la ventana
root.geometry("300x200")


# Función que se ejecutará al presionar el botón
def mostrar_mensaje():
    mensaje = entrada.get()  # Obtener el texto ingresado en el cuadro de texto
    if mensaje:
        messagebox.showinfo("Mensaje", f"Has escrito: {mensaje}")
    else:
        messagebox.showwarning("Advertencia", "El cuadro de texto está vacío")


# Crear un cuadro de texto donde el usuario puede ingresar datos
entrada = tk.Entry(root, width=30)
entrada.pack(pady=10)

# Crear un botón que mostrará el mensaje
boton = tk.Button(root, text="Mostrar mensaje", command=mostrar_mensaje)
boton.pack(pady=10)

# Ejecutar el loop principal para mostrar la ventana
root.mainloop()
