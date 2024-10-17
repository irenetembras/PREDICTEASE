import pandas as pd 
import sqlite3
import os
import pyexcel as p

# funcion para elegir el archivo
def elegir_archivo():
    print("por favor, ingrese la ruta del archivo (csv, excel, sqlite):")
    ruta_archivo = input()
    ruta_archivo = ruta_archivo.strip('\"\'')  # quitar comillas dobles y simples
    return ruta_archivo

# funcion para convertir los tipos de datos
def convertir_datos(datos):
    try:
        # convertir las columnas numericas
        for col in datos.select_dtypes(include=['object']).columns:
            try:
                datos[col] = pd.to_numeric(datos[col])
            except ValueError:
                pass  # si ocurre un error, dejamos el valor original
        # convertir las columnas de fechas
        for col in datos.columns:
            try:
                datos[col] = pd.to_datetime(datos[col], format='%Y-%m-%d')
            except (ValueError, TypeError):
                pass  # si ocurre un error, dejamos el valor original
        print("conversion de columnas numericas y de fecha realizada.")
    except Exception as e:
        print(f"error al convertir los tipos de datos: {e}")

# funcion para leer archivos excel (.xls) con pyexcel
def leer_excel(ruta_archivo):
    try:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        records = p.get_records(file_name=ruta_archivo)
        datos = pd.DataFrame(records)
        print("vista previa de los datos excel:")
        print(datos.head())
        convertir_datos(datos)
    except Exception as e:
        print(f"error al leer el archivo excel: {e}")

# funcion para leer archivos .xlsx con openpyxl
def leer_excel_xlsx(ruta_archivo):
    try:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        datos = pd.read_excel(ruta_archivo, engine='openpyxl')
        print("vista previa de los datos excel:")
        print(datos.head())
        convertir_datos(datos)
    except Exception as e:
        print(f"error al leer el archivo excel: {e}")

# funcion para leer archivos csv
def leer_csv(ruta_archivo):
    try:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        datos = pd.read_csv(ruta_archivo)
        print("vista previa de los datos csv:")
        print(datos.head())
        convertir_datos(datos)
    except Exception as e:
        print(f"error al leer el archivo csv: {e}")

# funcion para leer bases de datos sqlite
def leer_sqlite(ruta_archivo):
    try:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        conn = sqlite3.connect(ruta_archivo)
        consulta = "select name from sqlite_master where type='table';"
        nombre_tabla = pd.read_sql(consulta, conn).iloc[0, 0]
        datos = pd.read_sql(f"select * from {nombre_tabla}", conn)
        print("vista previa de los datos sqlite:")
        print(datos.head())
        convertir_datos(datos)
        conn.close()
    except Exception as e:
        print(f"error al leer la base de datos sqlite: {e}")

# funcion principal para ejecutar el programa
def main():
    ruta_archivo = elegir_archivo()

    if not os.path.exists(ruta_archivo):
        print("el archivo no existe. verifique la ruta.")
        return

    extension = os.path.splitext(ruta_archivo)[1].lower()

    if extension == ".csv":
        leer_csv(ruta_archivo)
    elif extension == ".xls":
        leer_excel(ruta_archivo)
    elif extension == ".xlsx":
        leer_excel_xlsx(ruta_archivo)
    elif extension in [".sqlite", ".db"]:
        leer_sqlite(ruta_archivo)
    else:
        print("formato de archivo no soportado. por favor, elija un archivo csv, excel o sqlite.")

if __name__ == "__main__":
    main()
