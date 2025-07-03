import socket
import time
import argparse
import ipaddress

def validar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Cliente UDP mejorado con validación y reintentos')
    parser.add_argument('--ip', default='127.0.0.1', help='IP del servidor (por defecto: localhost)')
    parser.add_argument('--port', type=int, default=12345, help='Puerto del servidor (por defecto: 12345)')
    parser.add_argument('--timeout', type=float, default=5.0, help='Timeout en segundos (por defecto: 5)')
    parser.add_argument('--family', choices=['ipv4', 'ipv6', 'auto'], default='auto',
                        help='Familia de direcciones (ipv4/ipv6/auto)')
    args = parser.parse_args()

    # Validación de parámetros
    if not validar_ip(args.ip):
        print(f"❌ Error: Dirección IP inválida: {args.ip}")
        return
        
    if not (1 <= args.port <= 65535):
        print(f"❌ Error: Puerto inválido {args.port}. Debe estar entre 1-65535")
        return

    print("="*50)
    print("📱 CLIENTE UDP MEJORADO")
    print("="*50)
    print(f"Conectando a {args.ip}:{args.port} | Timeout: {args.timeout}s")
    
    try:
        # Selección automática de familia de direcciones
        if args.family == 'auto':
            try:
                # Intentar conexión IPv6 primero
                socket.getaddrinfo(args.ip, args.port, socket.AF_INET6)
                family = socket.AF_INET6
                print("🔗 Usando stack IPv6")
            except socket.gaierror:
                family = socket.AF_INET
                print("🔗 Usando stack IPv4")
        else:
            family = socket.AF_INET6 if args.family == 'ipv6' else socket.AF_INET
            
        client_socket = socket.socket(family, socket.SOCK_DGRAM)
        client_socket.settimeout(args.timeout)
        
    except OSError as e:
        print(f"❌ Error crítico de socket: {e}")
        return
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return

    print("\n" + "="*50)
    print(f"✅ Conectado a {args.ip}:{args.port}")
    print("Escriba 'exit' para salir")
    print("="*50 + "\n")

    try:
        while True:
            mensaje = input("Ingrese mensaje >> ").strip()
            if not mensaje:
                continue
            if mensaje.lower() == "exit":
                break

            # Enviar con reintentos
            for intento in range(1, 4):  # 3 intentos
                try:
                    client_socket.sendto(mensaje.encode('utf-8'), (args.ip, args.port))
                    start = time.time()
                    
                    try:
                        respuesta, _ = client_socket.recvfrom(1024)
                        elapsed = round((time.time() - start) * 1000, 2)
                        print(f"🟢 Respuesta ({elapsed} ms): {respuesta.decode()}\n")
                        break  # Salir del bucle de reintentos
                        
                    except socket.timeout:
                        print(f"🔴 Timeout (intento {intento}/3): Sin respuesta del servidor")
                        if intento == 3:
                            print("✖️ Servidor no responde después de 3 intentos\n")
                            
                    except UnicodeDecodeError:
                        print("⚠️ Respuesta recibida no pudo ser decodificada\n")
                        break
                        
                except socket.error as e:
                    print(f"🚨 Error de red (intento {intento}/3): {e}")
                    if intento == 3:
                        print("✖️ Error persistente de red\n")
                    time.sleep(1)  # Esperar entre reintentos
                    
    except KeyboardInterrupt:
        print("\n🛑 Operación cancelada por el usuario")
    finally:
        client_socket.close()
        print("🔌 Conexión cerrada")

if __name__ == "__main__":
    main()