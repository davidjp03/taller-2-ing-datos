#Example: I/O bound descargar varios hilos en paralelo usando threading

import threading
import time

def download_file(file_id):
    print(f"Starting download of file {file_id}")
    time.sleep(2)  # Simula el tiempo de descarga
    print(f"Finished download of file {file_id}")

threads = []

for i in range(5):
    thread = threading.Thread(target=download_file, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
