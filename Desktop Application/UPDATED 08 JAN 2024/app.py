import cv2
import threading
import socket
import pyautogui
import time
import struct
import numpy as np
import re
import os
from login import FirebaseAuthentication

firebase_auth = FirebaseAuthentication()

windows_width, windows_height = pyautogui.size()
android_width = 0
android_height = 0

# Variable to store the latest frame
frame_lock = threading.Lock()
latest_frame = None

flag = True

def handle_file(file_name):

    print('File Handling')

    print(firebase_auth.userId)

    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_name):
        print(f"The file at '{file_name}' exists.")
        firebase_auth.upload_file(file_name)
    else:
        print(f"The file at '{file_name}' does not exist.")


# Function to capture frames
def capture_frames():
    while flag:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)

        # Resize the frame to the specified dimensions
        frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        # Update the latest frame
        global latest_frame
        latest_frame = buffer

    print('stopping to capturing frames')

# Function to handle client connections
def handle_client(client_socket):
    frame_rate = 10
    try:
        while True:
            with frame_lock:
                # Get the latest frame
                frame = latest_frame
                frame_size = len(frame)
                client_socket.send(struct.pack('!I', frame_size))
                # Send the frame data
                client_socket.sendall(frame)
                time.sleep(1.0/frame_rate)

        client_socket.close()
    except:
        print("end..")

def receive_data(client_socket):
    try:
        while flag:
            data = client_socket.recv(1024).decode("utf-8", errors='replace')
            if not data:
                print('end to receive data')
                break

            if '[PATH]' in data:
                _, x = data.split(',')
                #print(f'path {x}')

                file_thread = threading.Thread(target=handle_file, args=(x,))
                file_thread.start()

            elif '[SCROLL]' in data:
                _, x = data.split(',')
                pyautogui.scroll(int(x)) 

            elif '[KEY]' in data:
                _, x = data.split(',')

                if '[EN]' in data:
                    pyautogui.press('enter')
                elif '[BACK]' in data:
                    pyautogui.press('backspace')
                else:
                    pyautogui.write(x)

            elif '[SIZE]' in data:
                _, x, y = data.split(',')
                global android_width, android_height
                android_width = float(x) 
                android_height = float(y)
                print(x, y)
                # pyautogui.moveTo(x, y) 
                # pyautogui.onScreen(x, y)

            elif '[CURSOR]' in data:

                try:

                    _, x, y = data.split(',')

                    # print(screen_width, screen_height)
                    # print(screen_x, screen_y)

                    touch_x = float(x) 
                    touch_y = float(y)
                    # print(x, y)
                    # pyautogui.moveTo(x, y) 
                    # pyautogui.onScreen(x, y)

                    # Calculate the corresponding Windows screen coordinates
                    windows_x = (touch_x * windows_width) / android_width
                    windows_y = (touch_y * windows_height) / android_height

                    # print(windows_x, windows_y)
                    # print(windows_width, windows_height)
                    # print("\n")

                    # Move the mouse cursor to the adjusted coordinates on the Windows screen
                    pyautogui.moveTo(windows_x, windows_y, duration=0.1)
                    pyautogui.click(windows_x, windows_y)

                except Exception as err:
                    print(err)
            else:

                print("Received from client:", data)
    except Exception as err:
        print(f'end receive data.. {err}')


def init(server_socket):
    # Start capturing frames
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.start()
    global flag
    try:

        print("Server listening")
        #print(f"Server listening on {server_ip} : {server_port}")

        while flag:
            # Accept client connections
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

            receive_thread = threading.Thread(target=receive_data, args=(client_socket,))
            receive_thread.start()

    except:
        print("server end..")
        flag = False


