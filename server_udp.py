import socket
import signal
import sys
from datetime import datetime

# Configuración del servidor
SERVER_IP = '0.0.0.0'      # Escucha en todas las interfaces
SERVER_PORT = 12345        # Puerto de escucha
BUFFER_SIZE = 1024         # Tamaño del buffer de recepción

# Estadísticas de comunicación
stats = {
    'clientes_unicos': set(),
    'total_bytes': 0,
    'inicio': datetime.now(),
    'mensajes_por_cliente': {}
}

def cerrar_servidor(sig, frame):
    print("\n\n--- Estadísticas de Comunicación ---")
    print(f"Tiempo activo: {datetime.now() - stats['inicio']}")
    print(f"Clientes únicos: {len(stats['clientes_unicos'])}")
    print(f"Total de bytes recibidos: {stats['total_bytes']}")
    print("Mensajes por cliente:")
    for addr, count in stats['mensajes_por_cliente'].items():
        print(f"  {addr[0]}:{addr[1]} - {count} mensajes")
    print("\nCerrando servidor UDP...")
    server_socket.close()
    sys.exit(0)

# Manejar señal de interrupción para cierre controlado
signal.signal(signal.SIGINT, cerrar_servidor)

# Crear socket UDP IPv4
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
print(f"Servidor UDP escuchando en {SERVER_IP}:{SERVER_PORT}")
print("Presiona Ctrl+C para detener el servidor.\n")

while True:
    try:
        data, client_addr = server_socket.recvfrom(BUFFER_SIZE)
        stats['total_bytes'] += len(data)
        stats['clientes_unicos'].add(client_addr)
        stats['mensajes_por_cliente'][client_addr] = stats['mensajes_por_cliente'].get(client_addr, 0) + 1

        mensaje = data.decode('utf-8', errors='replace')
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {client_addr[0]}:{client_addr[1]} >> {mensaje}")

        respuesta = f"ACK: Recibido ({len(data)} bytes)"
        server_socket.sendto(respuesta.encode('utf-8'), client_addr)
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")