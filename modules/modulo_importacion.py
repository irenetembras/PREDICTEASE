import sqlite3
import pandas as pd


def import_file(file_path):
    """
    Function to load a csv, db, sqlite, xls or xlsx file.
    Handles cases where the file is corrupted, empty, or incompatible.
    """
    try:
        extension = file_path.split('.')[-1].lower()
        if extension == 'csv':
            df = pd.read_csv(file_path)
        elif extension in ['xlsx', 'xls']:
            df = pd.read_excel(file_path, engine='openpyxl')
        elif extension in ['sqlite', 'db']:
            conn = sqlite3.connect(file_path)
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';", conn
                )
            if tables.empty:
                raise ValueError("The file does not contain any tables.")
            table_name = tables['name'].iloc[0]
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
            conn.close()
        else:
            raise ValueError("The file does not contain any data.")

        # Validate that the DataFrame is not empty
        if df.empty:
            raise ValueError("The file does not contain any data.")

        # Validate that the columns contain the expected data types
        if not all(
            isinstance(val, (int, float, str)) for col in df.columns for val in df[col]
            ):
            raise ValueError("The file contains malformed or unreadable data.")
        return df

    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty or contains unreadable data.")
    except pd.errors.ParserError:
        raise ValueError("The file has an incorrect format or is corrupted.")
    except Exception as e:
        raise ValueError(f"Error reading the file: {str(e)}")
