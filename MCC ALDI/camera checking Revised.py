import PySimpleGUI as sg
import io
import base64
from PIL import Image
from datetime import datetime
import time
import cv2
import socket
import threading
import json
import os
from concurrent.futures import ThreadPoolExecutor

BORDER_COLOR = '#2c78c9'
DARK_HEADER_COLOR = '#010101'
img_HEIGHT = 650
img_WIDTH = 800
image_SIZE = (img_WIDTH, img_HEIGHT)

################  Icon  ########################
with open(r"C:\Users\aldif\OneDrive\Documents\Semester VII\Python\MCC vision System Rikho\logo.png", "rb") as img_file:
    iconb64 = base64.b64encode(img_file.read())
icon = iconb64
################################################

########### Function Popup Message #############

def get_popup(Message):
  sg.popup(Message, background_color='#282828',no_titlebar=True,icon = iconb64)

def get_popup_auto(Message):
  sg.popup_auto_close(Message, background_color='#282828',no_titlebar=True,icon = iconb64, auto_close_duration=1.5)

################################################

########### convert image to base64 image #############
def get_image64(filename):
    with open(filename, "rb") as img_file:
        image_data = base64.b64encode(img_file.read())
    buffer = io.BytesIO()
    imgdata = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(imgdata))
    new_img = img.resize(image_SIZE)  # x, y
    new_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    return img_b64

img_b64 = get_image64("Offline.png")
image_display = [[sg.Image(data=img_b64, pad=(0, 0), key='image')]]

################################################

############# Save image options ###############
set_file_saving = [sg.Column(
    [
        [sg.T('D I S P L A Y  I M A G E',
              font=('Helvetica', 18, "bold"),
              text_color='#000000',background_color=BORDER_COLOR)],
        [sg.CB('Enable Camera',
               font=('Helvetica', 12),
               enable_events=True,
               k='-isRealtime-',
               background_color=BORDER_COLOR)],
        [sg.T('Save Directory:',
              font=('Helvetica', 12),
              background_color=BORDER_COLOR)],
        [sg.Input(sg.user_settings_get_entry('-locImage-', ''),
                  key='-locImage-',
                  enable_events=True,
                  disabled=True,
                  use_readonly_for_disable=False,), sg.FolderBrowse()],
        [ sg.Button('Save Image', button_color=('#000000', '#d8ff34'),size=(13, 1))]
    ], pad=((0, 0), (0, 0)), background_color=BORDER_COLOR
)]

################################################

############# TCP/IP Settings ##################


set_tcp_ip = [sg.Column(
    [
        [sg.T('T C P / I P   C O N F I G', font=('Helvetica',
              18, "bold"),text_color='#000000', background_color=BORDER_COLOR)],
        [sg.CB('enable TCP', font=('Helvetica', 12), enable_events=True, k='-isTCPActive-',
               background_color=BORDER_COLOR, default=sg.user_settings_get_entry('-isTCPActive-', ''))],
        [sg.T('TCP Server IP : Port', font=('Helvetica', 12),
              background_color=BORDER_COLOR)],
        [sg.Input(sg.user_settings_get_entry('-IPSetting-', ''), key='-IPSetting-', size=(15, 1)),
         sg.T(':', font=('Helvetica', 12), background_color=BORDER_COLOR),
         sg.Input(sg.user_settings_get_entry('-PortSetting-', ''),
                  key='-PortSetting-', size=(10, 1)),
         sg.B('update', key='updateIpTcpServer')
         ]
    ], pad=((0, 0), (0, 0)), background_color=BORDER_COLOR
)]

################################################

cnt_setting = [set_file_saving,
               set_tcp_ip,
               ]

content_layout = [
       sg.Column(cnt_setting,
              size=(420, 650),
              pad=((0, 0), (0, 0)),
              background_color=BORDER_COLOR),
    sg.Column(image_display,
              size=image_SIZE,
              pad=((0, 0), (0, 0))
              )]

layout = [content_layout]



window = sg.Window('DVI - Decal Visual Inspection',
                   layout, finalize=True,
                   resizable=False,
                   no_titlebar=False,
                   margins=(0, 0),
                   grab_anywhere=True,
                    background_color='#e8ebf3',
                   icon=icon, location=(0, 0))

element_justification='c'

################################################

############## Camera Encoding #################
cap = cv2.VideoCapture(0)
cap.set(3, 800)
cap.set(4, 800)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

################################################


TCPEnable = 0
host = sg.user_settings_get_entry('-IPSetting-', '')
if sg.user_settings_get_entry('-PortSetting-', '') == "":
    port = 5000
else:
    port = int(sg.user_settings_get_entry('-PortSetting-', ''))
    
client_socket = socket.socket()  # instantiate

if TCPEnable:
    try:
        client_socket.connect((host, port))  # connect to the server
    except:
        get_popup("can not connect to server")


def receive_response(client_socket, directory, imageSaving):
    while True:
        try:
            # Menerima respons dari server
            response = client_socket.recv(1024)
            if response:
                print('Menerima respons: {}'.format(response.decode()))
                dataJson = json.loads(response.decode())

                if "request" in dataJson:
                    checking_request = dataJson["request"]
                    if checking_request == "checking":
                        save_image(client_socket, directory, imageSaving)
        except:
            break


def save_image(client_socket, directory, imageSaving):
    if values['-isRealtime-'] == True:
            ret, frame = cap.read()
            frameShow = cv2.resize(frame, image_SIZE)
            if imageSaving:
                now = datetime.now()
                filename = now.strftime("ObjectChecked_%Y%m%d%H%M%S%f") + ".png"
                new_file_name = os.path.join(directory, filename)
                cv2.imwrite(new_file_name, frameShow)
                get_popup_auto("Image Saved")
            imgbytesSend = cv2.imencode('.png', cv2.resize(frameShow, (800,600)))[1].tobytes()

    else:
        get_popup_auto("Camera is inactive! \nmake sure camera is enabled!")

    
#    TCPdataResponse = json.dumps(dataResponse)
#    client_socket.sendall(TCPdataResponse.encode())


def capture_image():
    ret, frame = cap.read()
    frame = cv2.resize(frame, image_SIZE)
    imgbytes = cv2.imencode('.png', frame)[1].tobytes()
    dataImage = base64.b64encode(imgbytes).decode('ascii')    
    content = base64.b64decode(dataImage)
    window['image'].update(data=content)

def DeactivateCamera():
    imageSample = get_image64("Offline.jpg")
    window['image'].update(data=imageSample)

camera_realtime = 0
directory = sg.user_settings_get_entry('-locImage-', '')
id = 5
# Buat objek ThreadPoolExecutor dengan jumlah thread yang sesuai
executor = ThreadPoolExecutor(max_workers=1)

while True:
    event, values = window.read(timeout=20)
    if event == 'EXIT' or event == sg.WIN_CLOSED:
        break  # exit button clicked

    if camera_realtime:
       capture_image()
    if event == '-locImage-':
        sg.user_settings_set_entry('-locImage-', values['-locImage-'])
        directory = sg.user_settings_get_entry('-locImage-', '')
        window['-isTCPActive-'].update(False)
        TCPEnable = False

    elif event == 'updateIpTcpServer':
        sg.user_settings_set_entry('-IPSetting-', values['-IPSetting-'])
        sg.user_settings_set_entry('-PortSetting-', values['-PortSetting-'])

        host = sg.user_settings_get_entry('-IPSetting-', '')
        port = int(sg.user_settings_get_entry('-PortSetting-', '')) 

    elif event == '-isTCPActive-':
        sg.user_settings_set_entry('-isTCPActive-', values['-isTCPActive-'])
        new_TCPEnable = sg.user_settings_get_entry('-isTCPActive-', '')
        if new_TCPEnable != TCPEnable:  # Check if TCPEnable changed
            TCPEnable = new_TCPEnable
            if TCPEnable:
                client_socket = socket.socket()  # instantiate
                try:
                    # connect to the server
                    client_socket.connect((host, port))
                except:
                    # Terjadi kesalahan, keluar dari loop
                     get_popup("Error 53 : Device can not conect to server \n please check LAN cables and TCP IP correctly!")
                     window['-isTCPActive-'].update(False)
            else:
                client_socket.close()
                window['-isTCPActive-'].update(False)
                

    elif event == '-isRealtime-':
        camera_realtime = values['-isRealtime-']
        if values['-isRealtime-'] == True:
            get_popup_auto("WARNING: Camera is ON")
        else:
            DeactivateCamera()
    elif event == 'Save Image':
       save_image(client_socket, directory, True)


# Release resources
executor.shutdown()
if TCPEnable:
    client_socket.close()
window.close()
