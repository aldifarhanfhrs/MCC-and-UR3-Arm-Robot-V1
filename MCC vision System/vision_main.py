import PySimpleGUI as sg
import time
import base64
from PIL import Image
import io
import socket
import threading
import json
import cv2
import numpy as np
import Jetson.GPIO as GPIO

width_display = (1920,1080)
BORDER_COLOR = '#194369'
DARK_HEADER_COLOR = '#112C45'

top_banner = [sg.Column([[
    sg.Text('MCC Vision System Checking', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(50,1),),
    sg.Text('' , font='Any 22', key='timetext', background_color=DARK_HEADER_COLOR, size=(49,1), justification='R')
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

imageSample = get_image64("images.jpg")
imageChange = get_image64("images1.png") 

img_b64 = imageSample
  
def createSetting():
   compItem = sg.Column([
          [ sg.Text('In Robot (P35)', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(16,1),),
            sg.Text(':', font=('Any 22'), background_color=DARK_HEADER_COLOR),
            sg.Text('0' , font='Any 22', key='inRobot', background_color=DARK_HEADER_COLOR)
          ],
          [ sg.Text('Out Confirm (P36)', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(16,1),),
            sg.Text(':', font=('Any 22'), background_color=DARK_HEADER_COLOR),
            sg.Text('0' , font='Any 22', key='outConfirm', background_color=DARK_HEADER_COLOR)
          ],
          [ sg.Text('Out Pass(P37)' , font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(16,1),),
            sg.Text(':', font=('Any 22'), background_color=DARK_HEADER_COLOR),
            sg.Text('0' , font='Any 22', key='outPass', background_color=DARK_HEADER_COLOR)
          ],
          [ sg.Text('Out Fail (P40)', font=('Any 22'), background_color=DARK_HEADER_COLOR, size=(16,1),),
            sg.Text(':', font=('Any 22'), background_color=DARK_HEADER_COLOR),
            sg.Text('0' , font='Any 22', key='outFail', background_color=DARK_HEADER_COLOR)
          ],
          [ sg.Text('Column2', background_color='green', size=(10,2)),
            sg.Button('capture', key='capture', button_color=('white', 'firebrick3'))                               
          ]],
          size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
   return compItem

def createComponet(deviceID): 
    compItem = sg.Column([[sg.T('Checking', font= fontTitle, background_color=BORDER_COLOR, size=sizeTitle, justification='c', pad = (0,0))], 
        [sg.T(deviceID + ':', font= fontText, background_color=DARK_HEADER_COLOR),
          sg.Input(sg.user_settings_get_entry('-dev1-', ''), key='-dev1-', size=(15, 1), font= fontText),
          sg.B('update', key='updDev1', font= fontText), 
          sg.T('Enable'  + ' ' * 6 + ':', font= fontText, background_color=DARK_HEADER_COLOR, pad = ((30,0),(0,0))),
          sg.CB('enable Device', font=fontText, enable_events=True, k='-enableDev-', background_color=DARK_HEADER_COLOR, default=sg.user_settings_get_entry('-enableDev-', ''))
        ], [sg.T('Result', font= fontResult, background_color=DARK_HEADER_COLOR, size=sizeResult, justification='c', pad = (0,0))],
        [sg.Image(data=img_b64, pad=(0, 0), key='image' + deviceID)]
      ],size=(itemWidth, itemHeight), background_color=DARK_HEADER_COLOR, pad = ((10, 0), (10, 0)))
    
    if deviceID == "config":
        compItem = createSetting()
     
    return compItem

#contTop = [frontItem, leftItem, rightItem]
deviceList = ('1', '2', '3')
contTop = [createComponet(deviceName) for deviceName in deviceList]

deviceList1 = ('4', '5', 'config')
contButtom = [createComponet(deviceName) for deviceName in deviceList1]

layout = [top_banner, contTop, contButtom]

window = sg.Window('MCC Visual Inspection',
                layout, finalize=True,
                resizable=True,
                no_titlebar=True,
                margins=(0, 0),
                grab_anywhere=True,
                location=(0, 0), right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)

# Create a TCP/IP socket
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.1.2'
port = 5000
server_address = ('192.168.1.2', 5000)
ServerSocket.bind(server_address)

# Listen for incoming connections
ServerSocket.listen(1)

captureRequest = 0

def on_new_client(client_socket, addr):
  
  status = "ok"
  try:
    thread = threading.Thread(target=sendData, args=(client_socket, addr))  # create the thread
    thread.start()  #
    dataAll = ""
    status = "ok"
    number = 0
    BUFF_SIZE = 1024
    while True:
      data = client_socket.recv(BUFF_SIZE).decode('utf-8')
      if not data:
        break        
      
      dataAll += data
      number += 1
      try:
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
        #print(f"{addr} >> {dataAll}")
        print(f"{addr} >> {number}")
        dataAll = ""
        number = 0
      except:         
        status = "reading"
        
      time.sleep(0.0001)  

    client_socket.close()
    thread.join()
  except:      
    status = "fail read data"
    print(status)

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
         print(f"disconnect {addr} ")
         break

def s_changes():
  while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    thread = threading.Thread(target=on_new_client, args=(Client, address))  # create the thread
    thread.start()  # start the thread` 1 `


thread = threading.Thread(target=s_changes)
thread.daemon = True
thread.start()

pinInpRobot = 35
pinConfirm = 36
pinPass = 37
pinFail = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pinInpRobot, GPIO.IN)
GPIO.setup([pinConfirm, pinPass, pinFail], GPIO.OUT)

dataRobotInput = 0

def checkDataIO(prevDataInp, prevCaptureRequest):
  actINRobot = GPIO.input(pinInpRobot)
  window['inRobot'].update(str(actINRobot))
  if actINRobot != prevDataInp:
    if  dataRobotInput == 0:
      prevCaptureRequest += 1 
      if prevCaptureRequest > 10:
        prevCaptureRequest = 0
      GPIO.output(pinConfirm, GPIO.HIGH)
      GPIO.output(pinPass, GPIO.HIGH)
      GPIO.output(pinFail, GPIO.LOW)

      window['outConfirm'].update("1")
      window['outPass'].update("1")
      window['outFail'].update("0")
      time.sleep(0.1)
    else:
      GPIO.output(pinConfirm, GPIO.LOW)
      GPIO.output(pinPass, GPIO.LOW)
      GPIO.output(pinFail, GPIO.LOW)
      window['outConfirm'].update("0")
      window['outPass'].update("0")
      window['outFail'].update("0")

    prevDataInp = actINRobot
  return [prevDataInp, prevCaptureRequest]


while True:    
  window['timetext'].update(time.strftime('%H:%M:%S'))
  event, values = window.read(timeout=50)

  dataRobotInput , captureRequest = checkDataIO(dataRobotInput, captureRequest)
  window['capture'].update(captureRequest)
  
  if event in (sg.WINDOW_CLOSED, 'Exit'):
      break    
  elif event == 'capture':
      captureRequest = captureRequest + 1
      if captureRequest > 10:
        captureRequest = 0
      print(captureRequest)

thread.join()   
ServerSocket.close()
window.close()