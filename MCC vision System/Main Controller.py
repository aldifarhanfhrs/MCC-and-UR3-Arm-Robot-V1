import PySimpleGUI as sg
import time
import base64
import pygame as pg
from PIL import Image
import io
import socket
import threading
import json
import cv2
import numpy as np

import tkinter as tk


pg.init()
info = pg.display.Info()

width_display = (info.current_w, info.current_h)
print(width_display)
#width_display = (1920,1080)
BORDER_COLOR = '#005AA9'
DARK_HEADER_COLOR = '#1B1B1F'

with open('logo MCC.png', 'rb') as img_file:
  iconb64 = base64.b64decode(img_file.read())
icon = iconb64


#hapus
'''
top_banner = [sg.Column([[
    sg.Text('MCC Vision System Checking', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(50,1),),
    sg.Text('' , font='Any 22', key='timetext', background_color=DARK_HEADER_COLOR, size=(61,1), justification='R')
]], size=(width_display[0], 50), pad = (0, 0), background_color=DARK_HEADER_COLOR
)]
'''
itemWidth = (width_display[0] - 32) / 3
itemHeight = (width_display[1] - 100) / 2
sizeTitle = (int(itemWidth * 162 / width_display[0]) , 1)
fontTitle = ('Roboto', 16)
fontText = ('Helvetica', 12)

sizeResult = (int(itemWidth * 500 / width_display[0]) , 1)
fontResult = ('Helvetica', 20)

def get_popup(Message):
  sg.popup_auto_close(Message, background_color='#282828', no_titlebar=True, icon= iconb64, auto_close_duration=2)
  
def get_error_popup(Message):
  sg.popup(Message, background_color='#282828', no_titlebar=True, icon=iconb64)

def get_image64(filename):
    with open(filename, "rb") as img_file:
        image_data = base64.b64encode(img_file.read())
    buffer = io.BytesIO()
    imgdata = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(imgdata))
    new_img = img.resize((800,600))  # x, y
    new_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    return img_b64

imageSample = get_image64("images.jpg")
imageChange = get_image64("images1.png") 

img_b64 = imageSample
  

def createComponet(deviceID, devicePosition, EnableCam, Image): 
    compItem = sg.Column([
      [sg.T(devicePosition, font= fontTitle, background_color=BORDER_COLOR, size=sizeTitle, justification='c', pad = (0,0))], 
        [sg.T('Camera' + deviceID, font= fontText, background_color=DARK_HEADER_COLOR),
#          sg.Input(sg.user_settings_get_entry('-dev1-', ''), key='-dev1-', size=(15, 1), font= fontText),
#          sg.B('update', key='updDev1', font= fontText), 
#          sg.T('Enable'  + ' ' * 6 + ':', font= fontText, background_color=DARK_HEADER_COLOR, pad = ((30,0),(0,0))),
          sg.CB('Enable ELP Cam', font=fontText, enable_events=True, key= EnableCam, background_color=DARK_HEADER_COLOR, default=False)
        ], [sg.T('Result', font= fontResult, background_color=DARK_HEADER_COLOR, size=sizeResult, justification='c', pad = (0,0))],
        [sg.Image(data=img_b64, pad=(0, 0), key='image' + deviceID)]
      ],size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
    
    if deviceID == "config":
        compItem = sg.Column([[sg.Text('Column2', background_color='green', size=(50,20)),
                               sg.Button('capture', button_color=('white', 'firebrick3'))                               
                            ]],
                size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
     
    return compItem
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#modifikasi

#contTop = [frontItem, leftItem, rightItem]
deviceList = ('1', '2', '3')
deviceLocation = ('T O P  C H E C K I N G', 'L E F T C H E C K I N G', 'B A CK  C H E C K I N G')
ImageCamera = ('Image01','Image02','Image03')
CamEnable = ('Cam01', 'Cam02', 'Cam03')
contTop = [createComponet(deviceName,deviceLocation,CamEnable,ImageCamera) for deviceName,deviceLocation,CamEnable,ImageCamera in zip(deviceList,deviceLocation,CamEnable,ImageCamera)]

deviceList1 = ('4', '5')
deviceLocation1 = ('B O T T O M  C H E C K I NG', 'R I G H T  C H E C K I N G')
CamEnable1 = ('Cam04', 'Cam05')
ImageCamera1 = ('Image04','Image05')
contButtom = [createComponet(deviceName,deviceLocation,CamEnable,ImageCamera) for deviceName,deviceLocation,CamEnable,ImageCamera in zip(deviceList1,deviceLocation1,CamEnable1,ImageCamera1)]

layout = [contTop, contButtom]

window = sg.Window('MCC Visual Inspection',
                layout, finalize=True,
                no_titlebar = True,
                margins = (0, 0),
                grab_anywhere = True,
                icon = icon,
                resizable=True,
                background_color= '#282828',
                element_justification= 'c',
                location=(0, 0), right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)
window.maximize()

def GetCamera(ScreenName,CameraPlacement):
  cam = cv2.VideoCapture(CameraPlacement)
  if cam is None or not cam.isOpened():
     get_error_popup("Camera is not detected \nmake sure to install correctly.")
  else:
    img_counter = 0
    ret, frame = cam.read()
    k = cv2.waitKey(1)
    frame = cv2.resize(frame, image_SIZE)
    imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    window[ScreenName].update(data=imgbytes)
  cam.release()

def DeactivateCamera(ScreenName):
  window[ScreenName].update(data=img_b64)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#modifikasi 


# Create a TCP/IP socket
ServerSocket = socket.socket()
host = '0.0.0.0'
port = 5000
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
ServerSocket.listen()

captureRequest = 0

def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data

def on_new_client(client_socket, addr):
  thread = threading.Thread(target=sendData, args=(client_socket, addr))  # create the thread
  thread.start()  #

  dataAll = recvall(client_socket)
  dataJson = json.loads(dataAll)
  deviceID = str(dataJson["data"]["deviceID"])
  my_bytes = dataJson["data"]["imageRaw"]
  imgbytes = base64.b64decode(my_bytes)
  
  #change image size
  base64Data = base64.b64encode(imgbytes)
  decoded_data = base64.b64decode(base64Data)
  np_data = np.fromstring(decoded_data,np.uint8)
  img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
  imgbytesSend = cv2.imencode('.png', cv2.resize(img, (650,400)))[1].tobytes()  # ditto
  dataImage = base64.b64encode(imgbytesSend).decode('ascii')

  window['image' + deviceID].update(data=dataImage)
  time.sleep(0.05)   

    
    
  client_socket.close()
  thread.join()

def sendData(client_socket, addr):  
  checkData = 0
  print(addr[0])
  while True:
    time.sleep(0.05)
    if checkData != captureRequest:
      try:
        checkData = captureRequest
        datajson = {"request" : "checking"}
        sendJson = json.dumps(datajson)
        client_socket.sendall(sendJson.encode())
        print("changeData")
      except:
         print("disconnect")
         break

def s_changes():
  while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    thread = threading.Thread(target=on_new_client, args=(Client, address))  # create the thread
    thread.start()  # start the thread

thread = threading.Thread(target=s_changes)
thread.daemon = True
thread.start()

while True:    
  window['timetext'].update(time.strftime('%H:%M:%S'))
  event, values = window.read(timeout=50)
  if event in (sg.WINDOW_CLOSED, 'Exit'):
      break    
  elif event == 'capture':
      captureRequest = captureRequest + 1
      print(captureRequest)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#tambah program running camera
window.close()