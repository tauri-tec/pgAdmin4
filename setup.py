import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
        "include_files": ['app/postgres_admin_queries.py', 'app/__init__.py'],
  "packages": ["os", "wx", "app", "psycopg2", "sqlalchemy"],
  "excludes": ["tkinter", 'Tcl', 'Tk']
  }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "PgAdmin4",
        version = "0.1",
        description = "The awesomest postgres tool!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("app/PgAdmin4.py", base=base)])

