from PyQt5.QtCore import QThread, pyqtSignal
import os
import requests
import shutil
import zipfile
import datetime

class UpdateWorker(QThread):
    end = pyqtSignal()
    success = pyqtSignal(str, str, str)
    error = pyqtSignal(Exception)

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo

    def run(self):
        try:
            current_version = self.get_local_version()
            latest_version = self.get_latest_version()

            if(current_version == latest_version['name']):
                self.end.emit()
                return

            if(not 'assets' in latest_version or len(latest_version['assets']) == 0):
                raise Exception("Nenhum asset encontrado na atualização.")

            download_url = latest_version['assets'][0]['browser_download_url']
            self.download_new_version(download_url, latest_version['name'])
            self.apply_update('{}.zip'.format(latest_version['name']))
            self.write_new_version(latest_version['name'])

            date = latest_version['published_at']
            date = datetime.datetime.fromisoformat(date).strftime('%d/%m/%Y')
            self.success.emit(latest_version['name'], date, current_version)

        except Exception as e:
            self.error.emit(e)
            
    def get_local_version(self) -> str:
        if not os.path.isfile('resources/version.txt'):
            return None
        
        version_file = open('resources/version.txt', 'r')
        return version_file.read()
        

    def get_latest_version(self) -> str:
        api_url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            latest_release = response.json()
            return latest_release
        else:
            raise Exception("Failed to fetch the latest release")
        
    def download_new_version(self, url: str, version: str) -> str:
        with requests.get(url, stream=True) as r:
            zip_file = '{}.zip'.format(version)

            with open(zip_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return url

    def apply_update(self, zip_file_path: str):
        update_dir = "update_tmp"
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(update_dir)
        
        current_dir = os.getcwd()

        # Iterate over files in the temporary directory
        for root, dirs, files in os.walk(update_dir):
            # Calculate the relative path of the file within the update structure
            rel_path = os.path.relpath(root, update_dir)
            target_path = os.path.join(current_dir, rel_path)

            # Create directories if they don't exist in the target location
            for dir_name in dirs:
                target_dir_path = os.path.join(target_path, dir_name)
                os.makedirs(target_dir_path, exist_ok=True)

            # Copy files to the target directory, overwriting if they already exist
            for file_name in files:
                source_file = os.path.join(root, file_name)
                target_file = os.path.join(target_path, file_name)
                shutil.copy2(source_file, target_file)  # Overwrite if exists, add if not
        
        # Cleanup
        shutil.rmtree(update_dir)
        os.remove(zip_file_path)

    def add_or_replace_file(source_file, target_path):
        """
        Adds or replaces a file at the specified target path. Creates any missing
        directories in the path without overwriting existing folders.
        
        Parameters:
        - source_file (str): Path to the file in the update directory.
        - target_path (str): Target path where the file should be added or replaced.
        """
        # Get the directory path for the target file
        target_dir = os.path.dirname(target_path)

        # Create any missing directories in the target path without affecting existing folders
        os.makedirs(target_dir, exist_ok=True)

        # Copy or replace the source file to the target location
        shutil.copy2(source_file, target_path)  # copy2 preserves metadata

    def write_new_version(self, new_version):
        with open('resources/version.txt', 'w') as version_file:
            version_file.write(new_version)