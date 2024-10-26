import os
import subprocess
import serial.tools.list_ports
import time
import requests
from pymavlink import mavutil

# Carpetas donde se guardarán los firmwares
CUBE_ORANGE_FOLDER = "FW444_cubeOrange"
CUBE_ORANGE_PLUS_FOLDER = "FW444_cubeOrangePlus"

PARAM_FILE_1 = "H20_release_1.param"
PARAM_FILE_2 = "H20_release_2.param"

def find_mavlink_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "mavlink" in port.description.lower():
            print(f"Dispositivo Cube Orange encontrado en: {port.device}")
            return port.device
    print("No se encontró un dispositivo Cube Orange.")
    return None

def open_serial_port(port, baudrate=115200):
    try:
        mavlink_conn = mavutil.mavlink_connection(port, baud=baudrate)
        print(f"Conectado al puerto {port}")
        return mavlink_conn
    except Exception as e:
        print(f"Error abriendo el puerto serial {port}: {e}")
        return None

def send_parameter(mavlink_conn, param_name, param_value):
    try:
        param_value = float(param_value)
        mavlink_conn.mav.param_set_send(
            mavlink_conn.target_system, mavlink_conn.target_component,
            param_name.encode('utf-8'), param_value, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        print(f"Enviado {param_name} = {param_value}")
    except Exception as e:
        print(f"Error enviando el parámetro {param_name}: {e}")

def load_parameters_from_file(param_file, mavlink_conn):
    with open(param_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if not line.startswith('#') and line.strip():
                try:
                    param_name, param_value = line.split(',')
                    send_parameter(mavlink_conn, param_name.strip(), param_value.strip())
                except ValueError:
                    print(f"Línea inválida o incompleta: {line.strip()}")

def reboot_cube(mavlink_conn):
    print("Reiniciando el Cube Orange...")
    mavlink_conn.mav.command_long_send(
        mavlink_conn.target_system, mavlink_conn.target_component,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0,
        1, 0, 0, 0, 0, 0, 0)
    mavlink_conn.close()
    time.sleep(10)  # Esperar 10 segundos para que se complete el reinicio

def install_parameters(port, param_file_1, param_file_2):
    # Paso 1: Conectar con MAVLink y cargar parámetros
    mavlink_conn = open_serial_port(port)
    if mavlink_conn:
        mavlink_conn.wait_heartbeat()
        print(f"Sistema {mavlink_conn.target_system}, Componente {mavlink_conn.target_component}")

        # Cargar parámetros por primera vez
        load_parameters_from_file(param_file_1, mavlink_conn)
        reboot_cube(mavlink_conn)  # Reiniciar después de la primera instalación

        # Re-conectar y cargar parámetros nuevamente después del reinicio
        mavlink_conn = open_serial_port(port)
        if mavlink_conn:
            mavlink_conn.wait_heartbeat()
            load_parameters_from_file(param_file_2, mavlink_conn)
            reboot_cube(mavlink_conn)  # Reiniciar después de la segunda instalación
        else:
            print("No se pudo abrir el puerto serial después del reinicio.")
    else:
        print("No se pudo abrir el puerto serial.")

# Función principal
if __name__ == "__main__":
    start_time = time.time()
    mavlink_port = find_mavlink_port()
    if mavlink_port:
        # Instalar parámetros dos veces con reinicio entre cada uno
        install_parameters(mavlink_port, PARAM_FILE_1, PARAM_FILE_2)
    else:
        print("No se detectó el Cube Orange. Conéctalo y vuelve a intentarlo.")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Tiempo total para la instalación de parámetros: {duration:.2f} segundos")
