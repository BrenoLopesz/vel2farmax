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
update_installer = Executable(
    script="update_installer.py",
    # base=None,
    base="Win32GUI",
    icon="velide.ico",
    target_name="update.exe"
)
exe_debug = Executable(
    script="run_app.py",
    base=None,
    icon="velide.ico",
    target_name="debug.exe"
)

setup(
    name="Vel2Farmax",
    version="1.35",
    description="Middleware para conectar o Farmax com o Velide.",
    executables=[exe, main, exe_debug],
    options={
        "build_exe": {
            "packages":["fdb"],
        }
    }
)

setup(
    name="Vel2Farmax Installer",
    version="1.0",
    description="Instalador de atualizações do Vel2Farmax.",
    executables=[update_installer],
    options={
        "build_exe": {
            "packages":["fdb"],
            "build_exe": "installer"
        },
        
    }
)
