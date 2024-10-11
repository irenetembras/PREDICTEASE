import pandas as pd
import sqlite3
import os

# funcion para elegir el archivo
def elegir_archivo():
    print("ingresa por favor la ruta del archivo (csv, excel, sqlite) :")
    archivo_ruta = input()
    return archivo_ruta

# funcion para convertir los tipos de datos
def convertir_datos(datos):
    try:
        # convertir columnas numericas
        for col in datos.select_dtypes(include=['object']).columns:
            datos[col] = pd.to_numeric(datos[col], errors='ignore')  # intentar convertir en numerico
        
        # convertir columnas de fecha con formato especifico (ejemplo: yyyy-mm-dd)
        for col in datos.columns:
            datos[col] = pd.to_datetime(datos[col], format='%Y-%m-%d', errors='ignore')  # convertir en fecha si posible con formato
        
        print("conversion de las columnas numericas y de fecha hecha.")
    except Exception as e:
        print(f"error en la conversion de los tipos de datos: {e}")

# funcion para leer archivos csv
def leer_csv(archivo_ruta):
    try:
        pd.set_option('display.max_columns', None)  # mostrar todas las columnas
        pd.set_option('display.expand_frame_repr', False)  # evitar saltos de linea para las columnas
        datos = pd.read_csv(archivo_ruta)
        print("vista previa de los datos csv:")
        print(datos.head())
        convertir_datos(datos)  # convertir tipos de datos
    except Exception as e:
        print(f"error al leer el archivo csv: {e}")

# funcion para leer archivos excel
def leer_excel(archivo_ruta):
    try:
        pd.set_option('display.max_columns', None)  # mostrar todas las columnas
        pd.set_option('display.expand_frame_repr', False)  # evitar saltos de linea para las columnas
        datos = pd.read_excel(archivo_ruta)
        print("vista previa de los datos excel:")
        print(datos.head())
        convertir_datos(datos)  # convertir tipos de datos
    except Exception as e:
        print(f"error al leer el archivo excel: {e}")

# funcion para leer bases de datos sqlite
def leer_sqlite(archivo_ruta):
    try:
        pd.set_option('display.max_columns', None)  # mostrar todas las columnas
        pd.set_option('display.expand_frame_repr', False)  # evitar saltos de linea para las columnas
        conn = sqlite3.connect(archivo_ruta)
        consulta = "select name from sqlite_master where type='table';"
        nombre_tabla = pd.read_sql(consulta, conn).iloc[0, 0]  # obtener el primer nombre de tabla
        datos = pd.read_sql(f"select * from {nombre_tabla}", conn)
        print("vista previa de los datos sqlite:")
        print(datos.head())
        convertir_datos(datos)  # convertir tipos de datos
        conn.close()
    except Exception as e:
        print(f"error al leer la base de datos sqlite: {e}")

# funcion principal para ejecutar el programa
def main():
    archivo_ruta = elegir_archivo()

    if not os.path.exists(archivo_ruta):
        print("el archivo no existe. verifica la ruta.")
        return

    extension = os.path.splitext(archivo_ruta)[1].lower()

    if extension == ".csv":
        leer_csv(archivo_ruta)
    elif extension in [".xlsx", ".xls"]:
        leer_excel(archivo_ruta)
    elif extension in [".sqlite", ".db"]:
        leer_sqlite(archivo_ruta)
    else:
        print("formato de archivo no soportado. por favor elige un archivo csv, excel o sqlite.")

if _name_ == "_main_":
    main()