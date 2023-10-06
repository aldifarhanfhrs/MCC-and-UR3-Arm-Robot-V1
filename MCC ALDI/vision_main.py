import PySimpleGUI as sg
import time
import base64
from PIL import Image
import io
import socket
import threading
import json
import pickle

width_display = (1920,1000)
BORDER_COLOR = '#db0000'
DARK_HEADER_COLOR = '#000000'

top_banner = [sg.Column([[
    sg.Text('MCC Vision System Checking', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(50,1),),
    sg.Text('' , font='Any 22', key='timetext', background_color=DARK_HEADER_COLOR, size=(61,1), justification='R')
]], size=(width_display[0], 50), pad = (0, 0), background_color=DARK_HEADER_COLOR
)]

itemWidth = (width_display[0] - 40) / 3
itemHeight = (width_display[1] - 80) / 2
sizeTitle = (int(itemWidth * 162 / width_display[0]) , 1)
fontTitle = ('Helvetica', 16)
fontText = ('Helvetica', 12)

sizeResult = (int(itemWidth * 122 / width_display[0]) , 1)
fontResult = ('Helvetica', 20)

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

imageSample = get_image64(r"images.jpg")
imageChange = get_image64(r"images1.png") 

img_b64 = imageSample
  

def createComponet(deviceID): 
    compItem = sg.Column([[sg.T('Font Checking', font= fontTitle, background_color=BORDER_COLOR, size=sizeTitle, justification='c', pad = (0,0))], 
        [sg.T(deviceID + ':', font= fontText, background_color=DARK_HEADER_COLOR),
          sg.Input(sg.user_settings_get_entry('-dev1-', ''), key='-dev1-', size=(15, 1), font= fontText),
          sg.B('update', key='updDev1', font= fontText), 
          sg.T('Enable'  + ' ' * 6 + ':', font= fontText, background_color=DARK_HEADER_COLOR, pad = ((30,0),(0,0))),
          sg.CB('enable Device', font=fontText, enable_events=True, k='-enableDev-', background_color=DARK_HEADER_COLOR, default=sg.user_settings_get_entry('-enableDev-', ''))
        ], [sg.T('Result', font= fontResult, background_color=DARK_HEADER_COLOR, size=sizeResult, justification='c', pad = (0,0))],
        [sg.Image(data=img_b64, pad=(0, 0), key='image' + deviceID)]
      ],size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
    
    if deviceID == "config":
        compItem = sg.Column([[sg.Text('DECISION', background_color='red', size=(60,20)),
                               sg.Button('capture', button_color=('white', 'firebrick3'))                               
                            ]],
                size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
     
    return compItem

#contTop = [frontItem, leftItem, rightItem]
deviceList = ('1', '2', '3')
contTop = [createComponet(deviceName) for deviceName in deviceList]

deviceList1 = ('4', '5', 'config')
contButtom = [createComponet(deviceName) for deviceName in deviceList1]

layout = [top_banner, contTop, contButtom]

window = sg.Window('Pad Printing Visual Inspection Main',
                layout, finalize=True,
                resizable=True,
                no_titlebar=False,
                margins=(0, 0),
                grab_anywhere=True,
                location=(0, 0), right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)

# Create a TCP/IP socket
ServerSocket = socket.socket()
host = '127.0.0.1'
port = 5000
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
ServerSocket.listen()

captureRequest = 0

def on_new_client(client_socket, addr):
  thread = threading.Thread(target=sendData, args=(client_socket, addr))  # create the thread
  thread.start()  #
  
  while True:
    data = client_socket.recv(1000024).decode('utf-8')
    if not data:
        break
    print(f"{addr} >> {data}")

    try:
      dataJson = json.loads(data)
      deviceID = str(dataJson["data"]["deviceID"])
      my_bytes = dataJson["data"]["imageRaw"]
      imgbytes = base64.b64decode(my_bytes)
      window['image' + deviceID].update(data=imgbytes)
    except ValueError:
       print(ValueError)

    time.sleep(0.05)   
    
  client_socket.close()
  thread.join()



def sendData(client_socket, addr):  
  checkData = 0
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
  Client, address = ServerSocket.accept()
  print('Connected to: ' + address[0] + ':' + str(address[1]))
  thread = threading.Thread(target=on_new_client, args=(Client, address))  # create the thread
  thread.start()  # start the thread
  

while True:    
  window['timetext'].update(time.strftime('%H:%M:%S'))
  event, values = window.read(timeout=50)
  thread = threading.Thread(target=s_changes)
  thread.daemon = True
  thread.start()

  if event in (sg.WINDOW_CLOSED, 'Exit'):
      break    
  elif event == 'capture':
      captureRequest = captureRequest + 1
      print(captureRequest)
window.close()