import tkinter as tk


class MyApplication:
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

    def get_decimal_places(self, series):
        """
        Obtiene el número máximo de decimales de una serie de datos.

        :param series: Serie de datos
        (por ejemplo, una columna de un DataFrame de pandas).
        :return: El número máximo de decimales en los valores numéricos.
        """
        decimals = series.dropna().astype(str).str.split('.').str[1]
        return decimals.str.len().max() if not decimals.empty else 0

    def update_interface_for_model(self, formula, r2, mse):
        """
        Actualiza la interfaz para mostrar los detalles del modelo cargado.

        :param formula: La fórmula del modelo cargado.
        :param r2: El valor de R² (coeficiente de determinación) del modelo.
        :param mse: El valor de MSE (error cuadrático medio) del modelo.
        """
        # Elimina los detalles anteriores del modelo si existen.
        if hasattr(self, 'model_details') and self.model_details:
            self.model_details.destroy()

            # Oculta secciones innecesarias de la interfaz.
            self.file_path_label.pack_forget()
            self.table_frame_border.pack_forget()
            self.controls_frame_border.pack_forget()
            self.graph_frame_border.pack_forget()

            # Crea un nuevo marco para mostrar los detalles del modelo.
            self.model_details = tk.Frame(self.root, bg="white")
            self.model_details.pack(fill=tk.BOTH, expand=True)

            # Prepara la información del modelo en formato texto.
            model_info = (
                f"Formula: {formula}\n"
                f"R²: {r2}\n"
                f"MSE: {mse}\n\n"
                f"Description: {self.model_description}"
            )

            # Crea una etiqueta para mostrar los detalles del modelo.
            model_info_label = tk.Label(
                self.model_details,
                text=model_info,
                font=("Helvetica", 12),
                fg="black",
                justify="center",
                bg="white"
            )
            model_info_label.pack(pady=10, expand=True)

    def populate_selectors(self):
        """
        Rellena los selectores de columna con las columnas del DataFrame.
        Si el DataFrame es válido, actualiza los valores
        de los selectores de entrada y salida.
        """
        if self.df is not None:  # Si el DataFrame no es None.
            columns = list(self.df.columns)  # Obtiene columnas del DataFrame.
            self.input_selector['values'] = columns  # Actualiza entrada.
            self.output_selector['values'] = columns  # Actualiza salida.
