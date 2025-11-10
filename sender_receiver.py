import socket

def send_tcp_request(ip, port, message, timeout=10):
    try:
        # Create TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set timeout (shorter default)
        client_socket.settimeout(timeout)
        
        # Connect to the server
        client_socket.connect((ip, port))
        # print(f"Connected to {ip}:{port}")
        
        # Send data
        client_socket.send(message.encode('utf-8'))
        # print(f"Sent: {message}")
        
        # Try to receive response with short timeout
        try:
            response = client_socket.recv(4096)
            return response.decode('utf-8')
        except socket.timeout:
            # No response received - this is OK for some commands
            return None
        
    except socket.timeout:
        print("Connection timed out")
    except ConnectionRefusedError:
        print("Connection refused - server might be down")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Usage example
# ip = "169.254.156.89" 
# port = 5025           
# message = "*Idn?"
# message = message + "\n"

# send_tcp_request(ip, port, message)