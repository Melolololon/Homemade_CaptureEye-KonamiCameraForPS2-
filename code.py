import smbus
import cv2

# Camera Init
# Start
cap = cv2.VideoCapture(0)

# 分類器
cascade_path = cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# 特徴量読み込み
cascade = cv2.CascadeClassifier(cascade_path)

# End

global preVoltX,preVoltY
preVoltX = 0.0
preVoltY = 0.0

def Camera():
    ret, frame = cap.read()
    frame = cv2.flip(frame,1)
    faces = cascade.detectMultiScale(frame, scaleFactor=1.23, minNeighbors=3, minSize=(50, 50))
    
    maxSize= (0,0,0,0)
    for x, y, w, h in faces:
        if w > maxSize[2]:
            maxSize=(x,y,w,h)
    
    x = maxSize[0]
    y = maxSize[1]
    w = maxSize[2]
    h = maxSize[3]
    
    cv2.rectangle(frame, (x, y), (x+w, y+h), (127, 255, 0), 2)
    
    facePosition = [x+w/2, y+h/2]

    cv2.imshow('frame', frame)
    
    cv2.waitKey(1)
    
    return facePosition
    
    
def CalcVolt(facePositionX ,facePositionY):
    minPosX = 100 + 50
    maxPosX= 520 - 50
    minPosY = 100
    maxPosY= 340
    facePositionX = facePositionX - minPosX
    facePositionY = facePositionY - minPosY
    
    
    #print(facePositionX,facePositionY)
    
    volt = [0,0]
    magX = 4095 / (maxPosX - minPosX)
    magY = 4095 / (maxPosY - minPosY)
    volt[0] = facePositionX * magX
    volt[1] = facePositionY * magY
    #print(volt[0],volt[1])
    
    
    if volt[0] < 0:
        volt[0] = preVoltX
    elif volt[0] > 4095:
        volt[0] = preVoltX
    if volt[1] < 0:
        volt[1] = preVoltY
    elif volt[1] > 4095:
        volt[1] = preVoltY
        
    if facePositionX == 0.0:
        volt[0] = preVoltX
    if facePositionY == 0.0:
        volt[1] = preVoltY
    
    #print(facePositionX,facePositionY)
    print(volt[0],volt[1])

    return volt

# 4725のアドレス
dacAddress4725 = 0x61

# 4726のアドレス
dacAddress4726 = 0x60

# D/Aコンバーターに電圧情報をセットする関数
def SetVolt(voluNum,address):
   
    bus = smbus.SMBus(1)

    # 引数で指定したアドレスを代入
    dacAddress = address

    # 固定値(デフォルトだと0x40でいいらしい)
    defAdress = 0x40

    # 電圧情報(12Bit)の前8Bit(電圧情報は8Bitと4Bitで分けて送信)
    voltPre8Bit = 0x00

    # 電圧情報(12Bit)の後4Bit
    # (xxxx0000)(xxxxは数字)形式で指定すること。
    voltPear4Bit = 0x00

    # 電圧情報の前と後を合体
    voltPre8Bit = voluNum >> 4    
    voltPear4Bit = (voluNum & 0b000000001111) << 4
    volt12Bit = [voltPre8Bit,voltPear4Bit]
    
    #print(voluNum) 
    #print(volt12Bit)
    # 電圧情報を送信
    bus.write_i2c_block_data(dacAddress,defAdress,volt12Bit)

cameraUpdateTime = 0

# 更新処理
while True:
    
    # フレームを読み込む
    ret, frame = cap.read()
    if ret == True:
        # フレームを表示
        cv2.imshow('Webcam Live', frame)
    
    
    facePos = Camera()
    volt = CalcVolt(facePos[0],facePos[1])
    
    # 電圧の値を保存
    if volt[0] > 0.0 or volt[0] < 4095:
        preVoltX = volt[0]
        
    if volt[1] > 0.0 or volt[1] < 4095:
        preVoltY = volt[1]
    
    # 4725用の電圧の数値(0～4095で指定。0で0.0V。4095で3.3V)
    #voltNum4725 = int(volt[0])
    voltNum4725 = int(volt[1])
    # 4726用の電圧の数値(0～4095で指定。0で0.0V。4095で3.3V)
    voltNum4726 = int(volt[0])

    #print(voltNum4726,voltNum4725 )
    
    # 4725の電圧を送信 
    SetVolt(voltNum4725 ,dacAddress4725)
    # 4726の電圧を送信 
    SetVolt(voltNum4726 ,dacAddress4726)
    
    
    
    
    
    
    
    
    
    
    
