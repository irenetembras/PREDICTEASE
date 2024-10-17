
import dearpygui.dearpygui as dpg

# Función que se ejecuta al presionar el botón
def mostrar_mensaje(sender, app_data, user_data):
    # Obtenemos el texto ingresado en el cuadro de texto
    texto_ingresado = dpg.get_value(user_data)
    # Mostramos el texto en la consola o un mensaje dentro de la GUI
    print(f"Texto ingresado: {texto_ingresado}")
    dpg.set_value("mensaje_texto", f"Has ingresado: {texto_ingresado}")

# Iniciar la ventana principal
dpg.create_context()

# Crear la ventana
with dpg.window(label="Ventana Principal", width=400, height=300):
    
    # Cuadro de texto para ingresar datos
    dpg.add_input_text(label="Ingresa algo aquí", tag="cuadro_texto")
    
    # Botón que al presionar muestra el mensaje
    dpg.add_button(label="Mostrar Mensaje", callback=mostrar_mensaje, user_data="cuadro_texto")
    
    # Campo donde se mostrará el mensaje al presionar el botón
    dpg.add_text("", tag="mensaje_texto")

# Configurar y mostrar la ventana
dpg.create_viewport(title="Interfaz Gráfica con DearPyGui", width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()

# Limpiar al cerrar
dpg.destroy_context()
