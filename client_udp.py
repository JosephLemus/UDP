import socket
import time

def main():
    print("="*50)
    print("📱 CLIENTE UDP - CONFIGURACIÓN INICIAL")
    print("="*50)

    # Configuración de IP y puerto del servidor
    server_ip = input("IP del servidor [localhost]: ") or "127.0.0.1"
    try:
        server_port = int(input("Puerto del servidor [12345]: ") or 12345)
    except ValueError:
        print("❌ El puerto debe ser un número entero.")
        return

    timeout = 5  # segundos

    # Crear socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    print("\n" + "="*50)
    print(f"✅ Conectado a {server_ip}:{server_port}")
    print("Escriba 'exit' para salir")
    print("="*50 + "\n")

    try:
        while True:
            mensaje = input("Ingrese mensaje >> ")
            if mensaje.lower() == "exit":
                break

            # Enviar datagrama al servidor
            client_socket.sendto(mensaje.encode('utf-8'), (server_ip, server_port))
            start = time.time()
            try:
                # Esperar respuesta del servidor
                respuesta, _ = client_socket.recvfrom(1024)
                elapsed = round((time.time() - start) * 1000, 2)
                print(f"🟢 Respuesta ({elapsed} ms): {respuesta.decode()}\n")
            except socket.timeout:
                print(f"🔴 Timeout: No hay respuesta del servidor en {timeout} segundos.\n")
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
    finally:
        client_socket.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()