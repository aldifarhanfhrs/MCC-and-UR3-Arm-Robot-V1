import PySimpleGUI as sg
import time
import base64
import io
from PIL import Image
#capture
import cv2
import numpy as np
from datetime import datetime
import json
import os

import socket
import threading

sizeDisplay = (1920, 1080)
headerHeigh = 50
sizeSetting = 500
padding = 10
sizeImageGUI = (sizeDisplay[0] - sizeSetting - 2 * padding, sizeDisplay[1] - headerHeigh - 2 * padding)
sizeImageSaving = (1280, 960)
sizeImageSend = (400,300)
sizeSetting = (sizeSetting - padding, sizeDisplay[1] - headerHeigh - 2* padding)

def readIconFile(filename):
    with open(filename, "rb") as img_file:
        iconb64 = base64.b64encode(img_file.read())

    return iconb64

def readBottleImage(filename, sizeImage):
    with open(filename, "rb") as img_file:
        image_data = base64.b64encode(img_file.read())
    buffer = io.BytesIO()
    imgdata = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(imgdata))
    new_img = img.resize(sizeImage)  # x, y
    new_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    return img_b64
  
def makeWindow():
    BORDER_COLOR = '#194369'
    DARK_HEADER_COLOR = '#112C45'
    icon = readIconFile(r"logo MCC.png")
    
    top_banner = [sg.Column([[
          sg.Text('Vision System Camera Checking', font=('Any 22'),background_color=DARK_HEADER_COLOR, size=(50, 1),),
          sg.Text('', font='Any 22', key='timetext', background_color=DARK_HEADER_COLOR, size=(61, 1), justification='R')
      ]], size=(sizeDisplay[0], headerHeigh), pad=(0, 0), background_color=DARK_HEADER_COLOR)
    ]

    imageBottle = readBottleImage(r"bottleImage.jpg", sizeImageGUI)
    cnt_image = [[sg.Image(data=imageBottle, pad=(0, 0), key='image')]]

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
                  default=0)],
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
                  18, "bold"), background_color=BORDER_COLOR, k='-TCPTitle-')],
            [sg.CB('enable TCP', font=('Helvetica', 12), enable_events=True, k='-isTCPActive-',
                  background_color=BORDER_COLOR, default=1)],
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
    contentLayout = [
        sg.Column(cnt_image,
                  size=sizeImageGUI,
                  pad=((10, 10), (10, 10))
                  ),
        sg.Column(cnt_setting,
              size=sizeSetting,
              pad=((0, 10), (0, 0)),
              background_color=BORDER_COLOR) ]
    
    layout = [top_banner, contentLayout]

    window = sg.Window('Vision System Camera Checking', layout, finalize=True, resizable=True, no_titlebar=True, margins=(0, 0), grab_anywhere=True,icon=icon, 
                       location=(0, 0), right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)
    return window

window = makeWindow()

#program capture
realtime = 0

HIGH_VALUE = 10000
WIDTH = HIGH_VALUE
HEIGHT = HIGH_VALUE
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(width,height)

deviceName = sg.user_settings_get_entry('-deviceName-', '')
def capture_image():
    ret, frame = cap.read()
    frame = cv2.resize(frame, sizeImageGUI)
    imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    dataImage = base64.b64encode(imgbytes).decode('ascii')

    content = base64.b64decode(dataImage)

    decoded_data = base64.b64decode(dataImage)
    np_data = np.fromstring(decoded_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    imgbytesSend = cv2.imencode('.png', cv2.resize(img, (400, 300)))[1].tobytes()  # ditto
    dataImage = base64.b64encode(imgbytesSend).decode('ascii')

    # print(content)
    window['image'].update(data=content)

#TCP
id = 1
TCPEnable = True
isSaving = sg.user_settings_get_entry('-IPSetting-', '')
host = sg.user_settings_get_entry('-IPSetting-', '')
directory = sg.user_settings_get_entry('-locImage-', '')
if sg.user_settings_get_entry('-PortSetting-', '') == "":
    port = 5000
else:
    port = int(sg.user_settings_get_entry('-PortSetting-', ''))

client_socket = socket.socket() 

def receive_response(client_socket, directory, imageSaving):
    global TCPEnable
    startup = 0
    
    while True:
      if startup < 5:
        capture_image_and_save(client_socket, directory, False)
        time.sleep(1)
        startup += 1
      else:
        startup = 5
        if TCPEnable:
          window['-TCPTitle-'].update('Connect')
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
            window['-TCPTitle-'].update('disconnect')
            break
        else:
          window['-TCPTitle-'].update('disconnect')
          break 
      
def capture_image_and_save(client_socket, directory, imageSaving):    
    global deviceName
    ret, frame = cap.read()
    frameShow = cv2.resize(frame, sizeImageGUI)
    imgbytes = cv2.imencode('.png', frameShow)[1].tobytes()  # ditto
    window['image'].update(data=imgbytes)

    if imageSaving:
        now = datetime.now()
        framesave = cv2.resize(frame, sizeImageSaving)
        filename = deviceName + now.strftime("%Y%m%d%H%M%S%f") + ".jpg"
        new_file_name = os.path.join(directory, filename)
        cv2.imwrite(new_file_name, frame)
        #cv2.imwrite(new_file_name, framesave)

    imgbytesSend = cv2.imencode('.png', cv2.resize(frame, sizeImageSend))[1].tobytes()  # ditto
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
    client_socket.sendall(TCPdataResponse.encode())

if TCPEnable:
    try:
        client_socket.connect((host, port))  # connect to the server
        response_thread = threading.Thread(
            target=receive_response, args=(client_socket, directory, isSaving))
        response_thread.daemon = True
        response_thread.start()
    except:
        print("can not connect to server")


#gui window application
while True:
    window['timetext'].update(time.strftime('%H:%M:%S'))
    event, values = window.read(10)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break  # exit button clicked   

    if event == '-locImage-':
        sg.user_settings_set_entry('-locImage-', values['-locImage-'])
        directory = sg.user_settings_get_entry('-locImage-', '')

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
        new_TCPEnable = sg.user_settings_get_entry('-isTCPActive-', '')
        if new_TCPEnable != TCPEnable:  # Check if TCPEnable changed
            TCPEnable = new_TCPEnable
            if TCPEnable:
                client_socket = socket.socket()  # instantiate
                try:
                    # connect to the server
                    client_socket.connect((host, port))
                    response_thread = threading.Thread(
                        target=receive_response, args=(client_socket, directory, isSaving))
                    response_thread.daemon = True
                    response_thread.start()
                except:
                    # Terjadi kesalahan, keluar dari loop
                    print("can not connect to server")
            else:
                client_socket.close()

    elif event == '-isSaveImage-':
        sg.user_settings_set_entry('-isSaveImage-', values['-isSaveImage-'])
        isSaving = values['-isSaveImage-']
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

    if realtime:
        capture_image()  

  

window.close()