import serial.tools.list_ports
import subprocess
import os

MAVPROXY_PATH = r"C:\Users\EderGarciaBalaguera\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\mavproxy.py"

def find_mavlink_port():
    """Buscar el puerto Mavlink del Cube Orange"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "mavlink" in port.description.lower():
            print(f"Dispositivo Cube Orange encontrado en: {port.device}")
            return port.device
    print("No se encontró un dispositivo Cube Orange.")
    return None

if __name__ == "__main__":
    # Detectar el puerto Mavlink
    mavlink_port = find_mavlink_port()

    if mavlink_port:
        try:
            subprocess.run(
                [
                    "python", MAVPROXY_PATH, 
                    "--master", mavlink_port, 
                    "--console", "--map"
                ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error al iniciar MAVProxy: {e}")
    else:
        print("Conecta el Cube Orange y vuelve a intentarlo.")
