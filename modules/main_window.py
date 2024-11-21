import tkinter as tk


def __init__(self, root):
        """
        Inicializa la aplicación con la ventana principal (root).

        :param root: La ventana principal de tkinter.
        """
        self.root = root
        # Inicialización de otros atributos aquí,
        # como los widgets, DataFrame, etc.
        # ...

def reset_controls(self):
        """
        Resetea los selectores de entrada/salida y el campo de descripción.
        Limpia cualquier dato en los widgets de la interfaz.
        """
        self.input_selector.set('')  # Limpia el selector de entrada.
        self.output_selector.set('')  # Limpia el selector de salida.
        self.dtext.delete('1.0', tk.END)  # Elimina todo el texto.
        self.result_label.config(text='')  # Limpia el resultado.

def clear_graph(self):
        """
        Limpia el gráfico en el panel de gráficos eliminando todos los widgets.
        """
        for widget in self.graph_frame.winfo_children():
            widget.destroy()  # Borra los widgets del gráfico.

