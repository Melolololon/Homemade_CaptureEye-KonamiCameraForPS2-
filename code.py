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

def Camera():
    ret, frame = cap.read()

    #取り込んだ映像を反転

    frame = cv2.flip(frame,1)
    faces = cascade.detectMultiScale(frame, scaleFactor=1.23, minNeighbors=3, minSize=(50, 50))
    
    # 一番大きい顔を検出
    maxSize= (0,0,0,0)
    for x, y, w, h in faces:
        if w > maxSize[2]:
            maxSize=(x,y,w,h)
    
    x = maxSize[0]
    y = maxSize[1]
    w = maxSize[2]
    h = maxSize[3]
    
    # 一番大きい顔に枠を付ける
    cv2.rectangle(frame, (x, y), (x+w, y+h), (127, 255, 0), 2)
    
    # 顔の中心座標を格納
    facePosition = [x+w/2, y+h/2]

    cv2.imshow('frame', frame)
    
    cv2.waitKey(1)
    
    return facePosition
    
    
def CalcVolt(facePositionX ,facePositionY):
    
    # カメラのなるべく最大、最小に近い中心座標を確認し、各変数へ代入
    minPosX = 100
    maxPosX= 520
    minPosY = 100
    maxPosY= 340
    # 計算しやすいように、最小値を0になるよう減算
    facePositionX = facePositionX - minPosX
    facePositionY = facePositionY - minPosY
    
    
    # 座標を電圧に変換して代入
    volt = [0,0]
    magX = 4095 / (maxPosX - minPosX)
    magY = 4095 / (maxPosY - minPosY)
    volt[0] = facePositionX * magX
    volt[1] = facePositionY * magY
    #print(volt[0],volt[1])
    
    # 画面外に出たら中心になるように
    if facePositionX == 0:
        volt[0] = 4095 / 2
    if facePositionY == 0:
        volt[1] = 4095 / 2
    
    # 万が一最大値、最小値を超えた際に範囲内に収める
    if volt[0] < 0:
        volt[0] = 0
    elif volt[0] > 4095:
        volt[0] = 4095
    if volt[1] < 0:
        volt[1] = 0
    elif volt[1] > 4095:
        volt[1] = 4095
    

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
    
    # Camera関数の処理を行い、顔の中心座標を取得
    facePos = Camera()
    # 顔の中心座標を電圧へ変換
    volt = CalcVolt(facePos[0],facePos[1])
    
    
    # 4725用の電圧の数値(0～4095で指定。0で0.0V。4095で3.3V)
    voltNum4725 = int(volt[1])
    # 4726用の電圧の数値(0～4095で指定。0で0.0V。4095で3.3V)
    voltNum4726 = int(volt[0])
    
    # 4725の電圧を送信 
    SetVolt(voltNum4725 ,dacAddress4725)
    # 4726の電圧を送信 
    SetVolt(voltNum4726 ,dacAddress4726)
