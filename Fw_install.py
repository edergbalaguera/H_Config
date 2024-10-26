import os
import subprocess
import serial.tools.list_ports
import time
import requests
import fw_uploader as fw

# URLs de firmware para Cube Orange y Cube Orange+ version: copter stable 4.4.4
FIRMWARE_URL_CUBE_ORANGE = "https://firmware.ardupilot.org/Copter/stable-4.4.4/CubeOrange/arducopter.apj"
FIRMWARE_URL_CUBE_ORANGE_PLUS = "https://firmware.ardupilot.org/Copter/stable-4.4.4/CubeOrangePlus/arducopter.apj"

# Carpetas donde se guardarán los firmwares
CUBE_ORANGE_FOLDER = "FW444_cubeOrange"
CUBE_ORANGE_PLUS_FOLDER = "FW444_cubeOrangePlus"

def download_firmware(url, folder):
    """Descargar el firmware y guardarlo en la carpeta específica"""
    if not os.path.exists(folder):
        os.makedirs(folder)

    firmware_file = os.path.join(folder, "arducopter.apj")
    if os.path.exists(firmware_file):
        print(f"El firmware ya existe en {firmware_file}, no es necesario descargarlo de nuevo.")
        return firmware_file

    print(f"Descargando firmware desde {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(firmware_file, 'wb') as f:
            f.write(response.content)
        print(f"Firmware descargado y guardado en {firmware_file}")
    else:
        print(f"Error al descargar el firmware. Código de estado: {response.status_code}")
        return None
    return firmware_file

def find_device():
    """Buscar el estado del Cube Orange+ (bootloader o mavlink)"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "1058" in port.hwid and "mavlink" not in port.description.lower():
            return "bootloader", port.device  # Cube Orange+ en modo bootloader
        elif "1058" in port.hwid and "mavlink" in port.description.lower():
            return "mavlink", port.device  # Cube Orange+ en modo mavlink
    return None, None

def flash_firmware(firmware_path, port, mode):
    """Flashear el firmware según el modo del Cube Orange+"""
    if mode == "mavlink":
        # Crear instancia de uploader y reiniciar el Cube para cambiar al modo bootloader
        cube_uploader = fw.uploader(portname=port, baudrate_bootloader=115200, baudrate_flightstack=[115200,115200])
        if cube_uploader.send_reboot():
            print("Reinicio exitoso. Buscando el puerto del bootloader...")
            bootloader_port = fw.find_bootloader_port()
            if bootloader_port:
                print(f"Bootloader encontrado en {bootloader_port}. Iniciando instalación de firmware.")
                subprocess.run(
                    ["python", "fw_uploader.py", "--port", bootloader_port, firmware_path],
                    check=True
                )
            else:
                print("No se pudo encontrar el puerto del bootloader después del reinicio.")
    elif mode == "bootloader":
        # Si ya está en modo bootloader, iniciar instalación directamente
        print(f"Instalando firmware en el Cube Orange+ en modo bootloader en el puerto {port}.")
        subprocess.run(
            ["python", "fw_uploader.py", "--port", port, firmware_path],
            check=True
        )

# Función principal
if __name__ == "__main__":
    # Escanear dispositivos y decidir la acción
    start_time = time.time()
    mode, port = find_device()
    if mode and port:
        if mode == "mavlink":
            print(f"Dispositivo en modo Mavlink encontrado en el puerto {port}. Cambiando a modo bootloader...")
        elif mode == "bootloader":
            print(f"Dispositivo en modo Bootloader encontrado en el puerto {port}. Procediendo a la instalación...")

        # Determinar el firmware correcto y proceder a flashear
        firmware_path = download_firmware(FIRMWARE_URL_CUBE_ORANGE_PLUS, CUBE_ORANGE_PLUS_FOLDER) if mode == "bootloader" or mode == "mavlink" else None
        if firmware_path:
            flash_firmware(firmware_path, port, mode)
    else:
        print("No se encontró un dispositivo Cube Orange+ conectado.")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Tiempo total para la instalación de firmware: {duration:.2f} segundos")
