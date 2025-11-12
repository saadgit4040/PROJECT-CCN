"""
Module 8: Graceful Shutdown & Exception Handling
Safely closes sockets and stops threads on server exit.
"""

from modules.logger import log_event
from modules.message_handler import send_message


def shutdown_server(server_socket, active_clients, lock):
    """
    Gracefully shutdown server and close all connections.
    
    Args:
        server_socket: Server socket object
        active_clients: Dictionary of active clients
        lock: Threading lock
        
    Example:
        shutdown_server(server_socket, active_clients, lock)
    """
    log_event("SERVER", "Shutting down server...")
    
    # Close all client connections
    with lock:
        for username, (client_socket, address) in list(active_clients.items()):
            try:
                send_message(client_socket, "SERVER_SHUTDOWN")
                client_socket.close()
            except:
                pass
        active_clients.clear()
    
    # Close server socket
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
    
    log_event("SERVER", "Server shutdown complete")

