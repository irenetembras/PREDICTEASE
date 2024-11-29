import sqlite3
import pandas as pd


def read_csv(file_path):
    """Helper function to read CSV files."""
    return pd.read_csv(file_path)


def read_excel(file_path):
    """Helper function to read Excel files."""
    return pd.read_excel(file_path, engine='openpyxl')


def read_sqlite_or_db(file_path):
    """Helper function to read SQLite or DB files."""
    connection = sqlite3.connect(file_path)
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type = 'table';", connection
    )
    if tables.empty:
        raise ValueError("The file does not contain any tables.")
    table_name = tables['name'].iloc[0]
    data_frame = pd.read_sql_query(f'SELECT * FROM "{table_name}"', connection)
    connection.close()
    return data_frame


def validate_dataframe(data_frame):
    """Helper function to validate that the DataFrame
    is not empty and has valid data types."""
    if data_frame.empty:
        raise ValueError("The file does not contain any data.")

    # Validate that the DataFrame columns contain valid data types.
    if not all(isinstance(val, (int, float, str))
               for col in data_frame.columns for val in data_frame[col]):
        raise ValueError("The file contains malformed or unreadable data.")


def import_file(file_path):
    """
    Function to load a CSV, DB, SQLite, XLS, or XLSX file.
    Handles cases where the file is corrupted, empty, or incompatible.
    """
    try:
        # Extract the file extension and determine
        # the appropriate reader function.
        extension = file_path.split('.')[-1].lower()

        if extension == 'csv':
            data_frame = read_csv(file_path)
        elif extension in ['xlsx', 'xls']:
            data_frame = read_excel(file_path)
        elif extension in ['sqlite', 'db']:
            data_frame = read_sqlite_or_db(file_path)
        else:
            raise ValueError("Unsupported file format or empty file.")

        # Validate the data in the DataFrame.
        validate_dataframe(data_frame)

        return data_frame

    # Return None explicitly on error (empty, corrupt, or unsupported files).
    except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError):
        return None

    # Return None for any other unexpected errors.
    except Exception:
        return None
