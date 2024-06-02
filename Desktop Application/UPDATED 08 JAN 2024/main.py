import customtkinter as ctk
import tkinter.messagebox as tkmb
import firebase_admin
from firebase_admin import credentials
from firebase_admin import credentials, firestore
from PIL import Image, ImageTk
from app import init, firebase_auth
import threading
import socket

HOST = 'localhost'
PORT = 25565

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Terminate Window
def on_closing():
    if tkmb.askokcancel("Quit", "Do you want to quit?"):
        firebase_auth.set_device_status(False)
        firebase_auth.disconnect()
        server_socket.close()
        print('end..')
        
        main_window.quit()
        main_window.destroy() 

def on_close():
    app.quit()  
    app.destroy()  

# Login
def login():
    entered_email = user_entry.get()
    entered_password = user_pass.get()

    if firebase_auth.is_valid_user(entered_email, entered_password):
        tkmb.showinfo(title="Login Successful", message="You have logged in successfully")
        open_main_window(entered_email)
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Email and Password")
        user_pass.delete(0, 'end')

# Second Window
def open_main_window(username):
    app.withdraw()

    key = firebase_auth.getKey()

    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    if firebase_auth.set_ngrok_auth_token(key, PORT):

        firebase_auth.set_device_status(True)
        firebase_auth.setLocalhost(HOST)
        x, y = firebase_auth.connect_ngrok()

        key_label = ctk.CTkLabel(main_window, text=f'256-bit WEP Key : {key}', font=("Helvetica", 20))
        key_label.pack(pady=20)

        frame = ctk.CTkFrame(master=main_window)
        frame.pack(pady=20, padx=40, fill='both', expand=True)

        label = ctk.CTkLabel(master=frame, text=f"Welcome {username} to Desktop Stream!\n", font=("Helvetica", 16))
        label.pack(pady=12, padx=10)

        local = ctk.CTkLabel(frame, text=f"HOST {x} \t PORT {y}\n", font=("Helvetica", 16))
        local.pack() 

        content_label = ctk.CTkLabel(frame, text="Server started...", font=("Helvetica", 16))
        content_label.pack() 

        # client receive thread
        client_thread = threading.Thread(target=init, args=(server_socket,))
        client_thread.start()

        main_window.mainloop()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.title("Desktop Stream")
    app.geometry("900x500")
    app.protocol("WM_DELETE_WINDOW", on_close)

    main_window = ctk.CTk()
    main_window.title("Dashboard")
    main_window.geometry("900x500")
    main_window.protocol("WM_DELETE_WINDOW", on_closing)

    label = ctk.CTkLabel(app, text="Login", font=("Helvetica", 24))
    label.pack(pady=20)
    
    frame = ctk.CTkFrame(master=app)
    frame.pack(pady=20, padx=40, fill='both', expand=True)
    
    label = ctk.CTkLabel(master=frame, text='Desktop Stream', font=("Helvetica", 16))
    label.pack(pady=12, padx=10)

    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Email", font=("Helvetica", 14), width=200, height=42)
    user_entry.pack(pady=12, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*", font=("Helvetica", 14), width=200, height=42)
    user_pass.pack(pady=12, padx=10)

    button = ctk.CTkButton(master=frame, text='Login', command=login, font=("Helvetica", 14), width=200, height=42)
    button.pack(pady=12, padx=10)
    app.mainloop()