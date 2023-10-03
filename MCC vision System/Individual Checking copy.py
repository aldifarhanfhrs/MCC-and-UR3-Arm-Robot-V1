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
import numpy as np

    
BORDER_COLOR = '#194369'
DARK_HEADER_COLOR = '#112C45'
img_HEIGHT = 600
img_WIDTH = 800
img_Setting = 400
image_SIZE = (1280, 960)

with open("logo MCC.png", "rb") as img_file:
    iconb64 = base64.b64encode(img_file.read())
icon = iconb64

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

img_b64 = get_image64("images.jpg")

top_banner = [sg.Column([[
    sg.Text('MCC Vision System Checking' + ' ' * 66,
            font=('Any 22'), background_color=DARK_HEADER_COLOR),
    sg.Text('', font='Any 22', key='timetext',
            background_color=DARK_HEADER_COLOR)
]], size=(img_Setting + img_WIDTH + 30, 50), pad=((0, 0), (0, 0)), background_color=DARK_HEADER_COLOR
)]
cnt_image = [[sg.Image(data=img_b64, pad=(0, 0), key='image')]]

set_file_saving = [sg.Column(
    [
        [sg.T('Image Configuration', font=('Helvetica', 26, "bold"),
              background_color=BORDER_COLOR,)],
        [sg.T('Image Saving',
              font=('Helvetica', 18, "bold"),
              background_color=BORDER_COLOR)],
        [sg.CB('Realtime Video',
               font=('Helvetica', 12),
               enable_events=True,
               k='-isRealtime-',
               background_color=BORDER_COLOR,
               default=sg.user_settings_get_entry('-isRealtime-', ''))],
        [sg.CB('enable saving',
               font=('Helvetica', 12),
               enable_events=True,
               k='-isSaveImage-',
               background_color=BORDER_COLOR,
               default=sg.user_settings_get_entry('-isSaveImage-', ''))],
        [sg.T('File Location',
              font=('Helvetica', 12),
              background_color=BORDER_COLOR)],
        [sg.Input(sg.user_settings_get_entry('-locImage-', ''),
                  key='-locImage-',
                  enable_events=True,
                  disabled=True,
                  use_readonly_for_disable=False,), sg.FolderBrowse()]
    ], pad=((0, 0), (0, 0)), background_color=BORDER_COLOR
)]

set_tcp_ip = [sg.Column(
    [
        [sg.T('TCP/IP configuration', font=('Helvetica',
              18, "bold"), background_color=BORDER_COLOR)],
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

set_device_id = [sg.Column(
    [
        [sg.T('Device ID', font=('Helvetica', 16), background_color=BORDER_COLOR)],
        [sg.Input(sg.user_settings_get_entry('-deviceName-', ''), key='-deviceName-', size=(30, 1)),
         sg.B('update', key='updateDevice')]
    ], pad=((0, 0), (0, 0)), background_color=BORDER_COLOR
)]

Set_Checking_enable = [sg.Column(
    [
        [sg.T('Checking Enable',
              font=('Helvetica', 16),
              background_color=BORDER_COLOR)],
        [sg.CB('enable Checking',
               font=('Helvetica', 14),
               enable_events=True, k='-isCheckEnable-',
               background_color=BORDER_COLOR,
               default=sg.user_settings_get_entry('-isCheckEnable-', ''))]
    ], pad=((0, 0), (0, 0)), background_color=BORDER_COLOR
)]

set_column = [sg.Column(
    [
        [sg.T('Decision',
              size=(13, 1),
              font=('Helvetica', 35, "bold"),
              background_color=BORDER_COLOR,
              key='-decisionlabel-',
              justification='center')],
        [sg.T('',
              size=(9, 1),
              font=('Helvetica', 50, "bold"),
              background_color=BORDER_COLOR,
              text_color='#FF0000',
              justification='center')]
    ], background_color=BORDER_COLOR
)]


cnt_setting = [set_file_saving,
               set_tcp_ip,
               set_device_id,
               Set_Checking_enable,
               set_column
               ]

content_layout = [
    sg.Column(cnt_image,
              size=image_SIZE,
              pad=((10, 10), (10, 10))
              ),
    sg.Column(cnt_setting,
              size=(img_Setting, img_HEIGHT),
              pad=((0, 0), (0, 0)),
              background_color=BORDER_COLOR)]

layout = [top_banner, content_layout,
          [sg.Button('EXIT', button_color=('white', 'firebrick3')),
           sg.Button('capture', button_color=('white', 'firebrick3'))]]
window = sg.Window('MCC Visual Inspection',
                   layout, finalize=True,
                   resizable=True,
                   no_titlebar=True,
                   margins=(0, 0),
                   grab_anywhere=True,
                   icon=icon, location=(0, 0))

cap = cv2.VideoCapture(0)
cap.set(3, 800)
cap.set(4, 600)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

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
        print("can not connect to server")

# need receive {"checking_request" : true}


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
                        capture_image_and_save(
                            client_socket, directory, imageSaving)
        except:
            break



realtime = 0
isSaving = sg.user_settings_get_entry('-isSaveImage-', '')
directory = sg.user_settings_get_entry('-locImage-', '')
id = 2
deviceName = sg.user_settings_get_entry('-deviceName-', '')

def capture_image_and_save(client_socket, directory, imageSaving):
    ret, frame = cap.read()
    frameShow = cv2.resize(frame, image_SIZE)
    imgbytes = cv2.imencode('.png', frameShow)[1].tobytes()  # ditto

    window['image'].update(data=imgbytes)
    if imageSaving:
        now = datetime.now()
        filename = deviceName + now.strftime("%Y%m%d%H%M%S%f") + ".png"
        new_file_name = os.path.join(directory, filename)
        cv2.imwrite(new_file_name, frameShow)

    imgbytesSend = cv2.imencode('.png', cv2.resize(frameShow, (400,300)))[1].tobytes()  # ditto
    dataImage = base64.b64encode(imgbytesSend).decode('ascii')
    
    dataResponse = {
        "response": "complete",
        "data": {
            "deviceID": id,
            "deviceName": deviceName,
            "result": 0,
            "resultDescription": "good",
            "imageRaw": dataImage
        }
    }
    
    
    TCPdataResponse = json.dumps(dataResponse)
    print(TCPdataResponse)
    client_socket.sendall(TCPdataResponse.encode())

def capture_image():
    ret, frame = cap.read()
    frame = cv2.resize(frame, image_SIZE)
    imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    dataImage = base64.b64encode(imgbytes).decode('ascii') 

    
    content = base64.b64decode(dataImage)
    
    decoded_data = base64.b64decode(dataImage)
    np_data = np.fromstring(decoded_data,np.uint8)
    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    imgbytesSend = cv2.imencode('.png', cv2.resize(img, (400,300)))[1].tobytes()  # ditto
    dataImage = base64.b64encode(imgbytesSend).decode('ascii')

    
    #print(content)
    window['image'].update(data=content)


while True:
    window['timetext'].update(time.strftime('%H:%M:%S'))
    event, values = window.read(timeout=50)
    if event == 'EXIT' or event == sg.WIN_CLOSED:
        break           # exit button clicked

    if realtime:
        capture_image()

    if TCPEnable:
        response_thread = threading.Thread(
            target=receive_response, args=(client_socket, directory, isSaving))
        response_thread.daemon = True
        response_thread.start()

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
    elif event == 'updateDevice':
        sg.user_settings_set_entry('-deviceName-', values['-deviceName-'])
        deviceName = values['-deviceName-']
    elif event == '-isTCPActive-':
        sg.user_settings_set_entry('-isTCPActive-', values['-isTCPActive-'])
        TCPEnable = sg.user_settings_get_entry('-isTCPActive-', '')
        if TCPEnable:
            client_socket = socket.socket()  # instantiate
            try:
                client_socket.connect((host, port))  # connect to the server
            except:
                # Terjadi kesalahan, keluar dari loop
                print("can not connect to server")
        else:
            client_socket.close()

    elif event == '-isSaveImage-':
        sg.user_settings_set_entry('-isSaveImage-', values['-isSaveImage-'])
        isSaving = values['-isSaveImage-']
        print(isSaving)
    elif event == '-isCheckEnable-':
        sg.user_settings_set_entry(
            '-isCheckEnable-', values['-isCheckEnable-'])
        if values['-isCheckEnable-']:
            window['-decisionlabel-'].update('Decision')
        else:
            window['-decisionlabel-'].update('')

    elif event == '-isRealtime-':
        sg.user_settings_set_entry('-isRealtime-', values['-isRealtime-'])
        realtime = values['-isRealtime-']
    elif event == 'capture':
        capture_image()


window.close()
