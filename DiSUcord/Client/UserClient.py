
# -> Client Code for userside of DiSUcord created by Tolga Basak and Ulas Meric


from tkinter import Tk, Label, Entry, Button, Text, messagebox, Scrollbar, ttk
import socket
import threading
import time

class DiSUcordClient:
    def __init__(self, master):
        self.master = master
        self.master.title("DiSUcord Client")

        self.username_label = Label(master, text="Username:")
        self.username_label.pack()

        self.username_entry = Entry(master)
        self.username_entry.pack()

        self.ip_label = Label(master, text="Server IP:")
        self.ip_label.pack()

        self.ip_entry = Entry(master)
        self.ip_entry.pack()

        self.port_label = Label(master, text="Server Port:")
        self.port_label.pack()

        self.port_entry = Entry(master)
        self.port_entry.pack()

        self.connect_button = Button(master, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack()

        self.status_label = Label(master, text="")
        self.status_label.pack()

        self.disconnect_button = Button(master, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_button.pack()

        self.channel_label = Label(master, text="Select Channel:")
        self.channel_label.pack()

        self.channel_selection = ttk.Combobox(master, values=["IF 100", "SPS 101"], state="readonly")
        self.channel_selection.pack()

        self.message_entry = Entry(master)
        self.message_entry.pack()

        self.send_button = Button(master, text="Send Message", command=self.send_message, state="disabled")
        self.send_button.pack()

        self.subscribe_if100_button = Button(master, text="Subscribe IF 100", command=self.subscribe_if100, state="disabled")
        self.subscribe_if100_button.pack()

        self.unsubscribe_if100_button = Button(master, text="Unsubscribe IF 100", command=self.unsubscribe_if100, state="disabled")
        

        self.subscribe_sps101_button = Button(master, text="Subscribe SPS 101", command=self.subscribe_sps101, state="disabled")
        self.subscribe_sps101_button.pack()

        self.unsubscribe_sps101_button = Button(master, text="Unsubscribe SPS 101", command=self.unsubscribe_sps101, state="disabled")
        
        # IF 100 Channel Label
        self.if100_channel_label = Label(master, text="Channel - IF 100")
        self.if100_channel_label.pack()

        # Text box for IF 100 channel messages
        self.text_display_if100 = Text(master, height=10, width=50)
        self.text_display_if100.pack()
        self.if100_scrollbar = Scrollbar(master, command=self.text_display_if100.yview)
        self.if100_scrollbar.pack(side="right", fill="y")
        self.text_display_if100.config(yscrollcommand=self.if100_scrollbar.set)

        # SPS 101 Channel Label
        self.sps101_channel_label = Label(master, text="Channel - SPS 101")
        self.sps101_channel_label.pack()

        # Text box for SPS 101 channel messages
        self.text_display_sps101 = Text(master, height=10, width=50)
        self.text_display_sps101.pack()
        self.sps101_scrollbar = Scrollbar(master, command=self.text_display_sps101.yview)
        self.sps101_scrollbar.pack(side="right", fill="y")
        self.text_display_sps101.config(yscrollcommand=self.sps101_scrollbar.set)


        self.sock = None
        self.connected = False

    def connect_to_server(self):
        username = self.username_entry.get()
        server_ip = self.ip_entry.get()
        server_port = self.port_entry.get()

        if not username or not server_ip or not server_port.isdigit():
            messagebox.showerror("Error", "Please enter valid username, server IP, and server port.")
            return

        try:
            server_port = int(server_port)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((server_ip, server_port))

            # Send a message to check if the username is available
            self.sock.sendall(f"CHECK_USERNAME:{username}".encode())
            response = self.sock.recv(1024).decode()
            if response == "USERNAME_NOT_AVAILABLE":
                messagebox.showerror("Error", "Username already in use. Please choose a different one.")
                self.sock.close()
                return

            # Username is available, set the connection flag
            self.connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()

            # Enable/disable buttons
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
            self.send_button.config(state="normal")
            self.subscribe_if100_button.config(state="normal")
            self.unsubscribe_if100_button.config(state="disabled")
            self.subscribe_sps101_button.config(state="normal")
            self.unsubscribe_sps101_button.config(state="disabled")

            # Display success message
            self.status_label.config(text="Connected to server", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            self.status_label.config(text="Connection failed", fg="red")


    def send_message(self):
        if not self.connected:
            messagebox.showerror("Error", "Not connected to the server.")
            return

        username = self.username_entry.get()
        message = self.message_entry.get()
        channel = self.channel_selection.get()
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        if not channel:
            messagebox.showerror("Error", "Please select a channel.")
            return

        full_message = f"{channel} - {username}: {message}"

        self.sock.sendall(full_message.encode())
        self.message_entry.delete(0, 'end')


    def subscribe_if100(self):
        self.send_subscription("SUBSCRIBE_IF100")

    def unsubscribe_if100(self):
        self.send_subscription("UNSUBSCRIBE_IF100")

    def subscribe_sps101(self):
        self.send_subscription("SUBSCRIBE_SPS101")

    def unsubscribe_sps101(self):
        self.send_subscription("UNSUBSCRIBE_SPS101")

    def send_subscription(self, command):
        if not self.connected:
            messagebox.showerror("Error", "Not connected to the server.")
            return

        username = self.username_entry.get()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        command_with_spaces = command.replace("IF100", "IF 100").replace("SPS101", "SPS 101")
        full_command = f"{command_with_spaces}:{username}"
        self.sock.sendall(full_command.encode())
        
        # Update button text based on subscription status
        if command == "SUBSCRIBE_IF100":
            self.subscribe_if100_button.config(text="Unsubscribe IF 100", command=self.unsubscribe_if100)
            self.unsubscribe_if100_button.config(state="normal")
        elif command == "UNSUBSCRIBE_IF100":
            self.subscribe_if100_button.config(text="Subscribe IF 100", command=self.subscribe_if100)
            self.unsubscribe_if100_button.config(state="disabled")
        elif command == "SUBSCRIBE_SPS101":
            self.subscribe_sps101_button.config(text="Unsubscribe SPS 101", command=self.unsubscribe_sps101)
            self.unsubscribe_sps101_button.config(state="normal")
        elif command == "UNSUBSCRIBE_SPS101":
            self.subscribe_sps101_button.config(text="Subscribe SPS 101", command=self.subscribe_sps101)
            self.unsubscribe_sps101_button.config(state="disabled")

    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                full_message = data.decode()

                # Split the received message into channel and message content
                if " - " in full_message:
                    channel, message = full_message.split(" - ", 1)

                    # Display the message in the appropriate text display based on the channel
                    if channel == "IF 100":
                        self.text_display_if100.insert("end", message + '\n')
                    elif channel == "SPS 101":
                        self.text_display_sps101.insert("end", message + '\n')
                else:
                    print("Received message in an unknown format.")

            except Exception as e:
                print(f"Error receiving message: {str(e)}")
                break

    def disconnect(self):
        # Unsubscribe from channels
        if self.subscribe_if100_button.cget("text") == "Unsubscribe IF 100":
            self.send_subscription("UNSUBSCRIBE_IF100")
        time.sleep(0.1)
        if self.subscribe_sps101_button.cget("text") == "Unsubscribe SPS 101":
            self.send_subscription("UNSUBSCRIBE_SPS101")

        # Wait for a short time to ensure that unsubscribe messages are sent
        time.sleep(0.1)

        # Close the socket and reset UI
        if self.connected:
            self.sock.close()
            self.connected = False

            # Enable/disable buttons
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.send_button.config(state="disabled")
            self.subscribe_if100_button.config(state="disabled")
            self.unsubscribe_if100_button.config(state="disabled")
            self.subscribe_sps101_button.config(state="disabled")
            self.unsubscribe_sps101_button.config(state="disabled")

            # Clear status label
            self.status_label.config(text="")

    def on_closing(self):
        self.disconnect()
        self.master.destroy()

# Main part of the code
if __name__ == "__main__":
    root = Tk()
    client = DiSUcordClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()
