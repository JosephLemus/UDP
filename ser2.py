import socket
import signal
import sys
import os
import argparse
from datetime import datetime
import time

# Manejar argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Servidor UDP mejorado con soporte dual-stack IPv4/IPv6')
parser.add_argument('--ip', default=os.getenv('SERVER_IP', '::'),
                    help='Dirección IP para escuchar (por defecto: todas las interfaces)')
parser.add_argument('--port', type=int, default=os.getenv('SERVER_PORT', 12345),
                    help='Puerto para escuchar (por defecto: 12345)')
parser.add_argument('--buffer-size', type=int, default=os.getenv('BUFFER_SIZE', 1024),
                    help='Tamaño del buffer de recepción (por defecto: 1024)')
args = parser.parse_args()

# Validación de parámetros
if not (1 <= args.port <= 65535):
    print(f"❌ Error: Puerto inválido {args.port}. Debe estar entre 1-65535")
    sys.exit(1)

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
    if 'server_socket' in globals():
        server_socket.close()
    sys.exit(0)

# Registrar manejador de señales
signal.signal(signal.SIGINT, cerrar_servidor)

try:
    # Crear socket dual-stack (IPv4 + IPv6)
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # Habilitar IPv4
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Reutilizar dirección
    
    print(f"🔄 Iniciando servidor en [{args.ip}]:{args.port} (dual-stack IPv4/IPv6)")
    server_socket.bind((args.ip, args.port))
    print(f"✅ Servidor UDP escuchando en [{args.ip}]:{args.port}")
    print("Presiona Ctrl+C para detener el servidor\n")
    
except OSError as e:
    print(f"❌ Error crítico al iniciar servidor: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)

while True:
    try:
        data, client_addr = server_socket.recvfrom(args.buffer_size)
        stats['total_bytes'] += len(data)
        
        # Normalizar dirección IPv4-mapeada (::ffff:192.0.2.1 → 192.0.2.1)
        if client_addr[0].startswith('::ffff:'):
            normalized_addr = (client_addr[0][7:], client_addr[1])
        else:
            normalized_addr = (client_addr[0], client_addr[1])
            
        stats['clientes_unicos'].add(normalized_addr)
        stats['mensajes_por_cliente'][normalized_addr] = stats['mensajes_por_cliente'].get(normalized_addr, 0) + 1

        # Decodificación robusta con manejo de errores
        try:
            mensaje = data.decode('utf-8', errors='replace')
        except UnicodeDecodeError:
            mensaje = f"<Datos binarios: {len(data)} bytes>"

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {normalized_addr[0]}:{normalized_addr[1]} >> {mensaje}")

        # Enviar ACK con reintentos
        respuesta = f"ACK: Recibido ({len(data)} bytes)"
        for _ in range(3):  # 3 intentos de reenvío
            try:
                server_socket.sendto(respuesta.encode('utf-8'), client_addr)
                break
            except socket.error as e:
                print(f"⚠️ Error al enviar ACK (intento {_+1}/3): {e}")
                time.sleep(0.5)  # Esperar antes de reintentar
                
    except socket.timeout:
        continue  # Timeout de lectura, continuar normalmente
    except socket.error as e:
        print(f"🚨 Error de socket: {e}")
        time.sleep(1)  # Esperar antes de reintentar
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")