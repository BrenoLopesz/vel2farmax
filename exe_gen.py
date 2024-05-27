from cx_Freeze import setup, Executable

exe = Executable(
    script="main.py",
    base=None,
    #base="Win32GUI",
    icon="velide.ico"
)

setup(
    name="Vel2Farmax",
    version="1.0",
    description="Middleware para conectar o Farmax com o Velide.",
    executables=[exe],
    options={
        "build_exe": {
            "packages":["fdb"]
        }
    }
)
