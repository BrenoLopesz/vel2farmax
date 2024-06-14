import time
import subprocess
import os
import sys

def run_app():
    try:
        # Determine the directory of the frozen executable
        if getattr(sys, 'frozen', False):
            # The application is frozen
            application_path = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            application_path = os.path.dirname(__file__)
        
        main_script = os.path.join(application_path, "main.exe")
        subprocess.run([main_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Application crashed with error: {e}. Restarting...")
        time.sleep(5)  # Wait for 5 seconds before restarting
        run_app()

if __name__ == "__main__":
    run_app()