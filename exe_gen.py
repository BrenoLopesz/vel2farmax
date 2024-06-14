from cx_Freeze import setup, Executable

# Runs the run_app.py file (restart if fails)
exe = Executable(
    script="run_app.py",
    # base=None,
    base="Win32GUI",
    icon="velide.ico",
    target_name="Vel2Farmax.exe"
)
# The remaining code, does not restart if fails
main = Executable(
    script="main.py",
    # base=None,
    base="Win32GUI",
    icon="velide.ico",
    target_name="main.exe"
)
exe_debug = Executable(
    script="run_app.py",
    base=None,
    icon="velide.ico",
    target_name="debug.exe"
)

setup(
    name="Vel2Farmax",
    version="1.0",
    description="Middleware para conectar o Farmax com o Velide.",
    executables=[exe, main, exe_debug],
    options={
        "build_exe": {
            "packages":["fdb"],
        }
    }
)
