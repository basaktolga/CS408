
# -> Server Code of DiSUcord created by Tolga Basak and Ulas Meric


import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

class DiSUcordServer:
    def __init__(self, master):
        self.master = master
        self.master.title("DiSUcord Server")

        self.port_label = tk.Label(master, text="Port:")
        self.port_label.pack()

        self.port_entry = tk.Entry(master)
        self.port_entry.pack()
        self.port_entry.insert(0, "12345")  # Default port value

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop Server", command=self.stop_server, state="disabled")
        self.stop_button.pack()

        self.log = scrolledtext.ScrolledText(master, height=10, width=50, state="disabled")
        self.log.pack()

        # Text boxes for displaying clients and subscribers
        self.connected_clients_label = tk.Label(master, text="Connected Clients:")
        self.connected_clients_label.pack()
        self.connected_clients_text = scrolledtext.ScrolledText(master, height=5, width=30)
        self.connected_clients_text.pack()

        self.if100_subscribers_label = tk.Label(master, text="IF 100 Subscribers:")
        self.if100_subscribers_label.pack()
        self.if100_subscribers_text = scrolledtext.ScrolledText(master, height=5, width=30)
        self.if100_subscribers_text.pack()

        self.sps101_subscribers_label = tk.Label(master, text="SPS 101 Subscribers:")
        self.sps101_subscribers_label.pack()
        self.sps101_subscribers_text = scrolledtext.ScrolledText(master, height=5, width=30)
        self.sps101_subscribers_text.pack()

        self.server_socket = None
        self.clients = {}  # Maps usernames to client sockets
        self.channels = {"IF 100": set(), "SPS 101": set()}

    def log_message(self, message):
        self.log.config(state="normal")
        self.log.insert("end", message + "\n")
        self.log.config(state="disabled")
        self.log.see("end")

    def start_server(self):
        port = self.port_entry.get()
        if not port.isdigit():
            messagebox.showerror("Error", "Invalid port number.")
            return

        port = int(port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            threading.Thread(target=self.accept_connections, daemon=True).start()
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.log_message(f"Server started on port {port}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("Server stopped.")
        self.clients.clear()
        self.channels = {"IF 100": set(), "SPS 101": set()}
        self.update_client_lists()

    def accept_connections(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                self.log_message(f"Server stopped accepting connections: {str(e)}")
                break

    def handle_client(self, client_socket):
        username_received = False
        username = None
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    if username:
                        self.remove_client(username, client_socket)
                    break
                message = data.decode()

                if not username_received:
                    if message.startswith("CHECK_USERNAME:"):
                        username = message.split(":", 1)[1]
                        self.handle_username(client_socket, username)
                        username_received = True
                    else:
                        self.log_message(f"Unexpected message format from new client: {message}")
                else:
                    self.process_message(client_socket, message)

            except Exception as e:
                self.log_message(f"Error: {str(e)}")
                if username:
                    self.remove_client(username, client_socket)
                break

    def remove_client(self, username, client_socket):
        # Remove the client from the clients list and all channels
        if username in self.clients:
            del self.clients[username]

        for channel in self.channels.values():
            if client_socket in channel:
                channel.remove(client_socket)

        self.update_client_lists()
        self.log_message(f"{username} has disconnected.")



    def handle_username(self, client_socket, username):
        if username in self.clients:
            client_socket.sendall("USERNAME_NOT_AVAILABLE".encode())
        else:
            self.clients[username] = client_socket
            client_socket.sendall("USERNAME_AVAILABLE".encode())
            self.update_client_lists()

    def process_message(self, client_socket, message):
        if message.startswith("CHECK_USERNAME:"):
            username = message.split(":", 1)[1]
            if username in self.clients:
                client_socket.sendall("USERNAME_NOT_AVAILABLE".encode())
            else:
                self.clients[username] = client_socket
                client_socket.sendall("USERNAME_AVAILABLE".encode())
                self.update_client_lists()
        elif message.startswith("SUBSCRIBE_") or message.startswith("UNSUBSCRIBE_"):
            self.handle_subscription(client_socket, message)

        else:
            if " - " in message:
                channel, msg = message.split(" - ", 1)
                if channel in self.channels and client_socket in self.channels[channel]:
                    self.broadcast_message(channel, msg)
                else:
                    client_socket.sendall(f"You are not subscribed to {channel}".encode())
            else:
                # Handle case where message does not contain " - "
                self.log_message(f"Invalid message format received: {message}")

    def handle_subscription(self, client_socket, message):
        command, username = message.split(":", 1)
        channel = command.split("_")[1]
        if "UNSUBSCRIBE" in command:
            self.channels[channel].discard(client_socket)
            self.log_message(f"{username} unsubscribed from {channel}")
        elif "SUBSCRIBE" in command:
            self.channels[channel].add(client_socket)
            self.log_message(f"{username} subscribed to {channel}")
        self.update_client_lists()

    def broadcast_message(self, channel, message):
        for client in self.channels[channel]:
            try:
                client.sendall(f"{channel} - {message}".encode())
            except Exception as e:
                self.log_message(f"Error sending message: {str(e)}")

    def update_client_lists(self):
        # Update the connected clients list
        connected_clients = [username for username in self.clients.keys()]
        self.connected_clients_text.delete("1.0", tk.END)
        self.connected_clients_text.insert(tk.END, "\n".join(connected_clients))

        # Update the IF 100 subscribers list
        if100_subscribers = [username for username, client in self.clients.items() if client in self.channels["IF 100"]]
        self.if100_subscribers_text.delete("1.0", tk.END)
        self.if100_subscribers_text.insert(tk.END, "\n".join(if100_subscribers))

        # Update the SPS 101 subscribers list
        sps101_subscribers = [username for username, client in self.clients.items() if client in self.channels["SPS 101"]]
        self.sps101_subscribers_text.delete("1.0", tk.END)
        self.sps101_subscribers_text.insert(tk.END, "\n".join(sps101_subscribers))

# Main part of the code
if __name__ == "__main__":
    root = tk.Tk()
    server = DiSUcordServer(root)
    root.mainloop()
