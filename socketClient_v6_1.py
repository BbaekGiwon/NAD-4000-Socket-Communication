###################################################################
# v6_1 update
## v6_0는 v5의 방식을 유지하면서 슬라이싱 방식으로 변환하였다면 v6_1는 오직 슬라이싱에만 의존하는 버전
###################################################################

# 소켓을 사용하기 위해서는 socket을 import해야 한다.
import socket              
import threading
# 날짜 계산을 위한 라이브러리
from datetime import datetime
# 시간이 조금 지난 뒤 다시 메세지를 보내기 위함
import time

# import codecs

# 로컬은 127.0.0.1의 ip로 접속한다.
# 푸른솔 ip
# HOST = '182.217.213.12'  
# 토종된장 ip
HOST = '121.189.210.41'
# 푸드팜 ip
# HOST = '121.189.201.104'
# 아라리 ip
# HOST = '121.189.142.56'
# port는 위 서버에서 설정한 9999로 접속을 한다.
PORT = 8120

# 입력값을 hex형식으로 변환하는 함수 <- 문자열 입력, 리스트 반환
def decode_string_to_hex(data):
  # 리턴 변수
  return_list = []
    
  # data를 순환하면서 검사
  for i in data:
    return_list.append(format(i, '02x').upper() + ":")
  # mfc값이 대문자이므로 대문자 변환
  return return_list

# CMD가 3A일 때 날짜 변환 함수, 두 자리 형식으로 반환 -> ex)1이라면 01로 반환
# parameter: date_from, date_to="%Y/%m/%d"
def cal_send_DATA_CMD_3A(date_from, date_to):
  # 반환 변수
  hex_date = ""
  
  # 날짜를 6byte 16진수로 변환
  for i in date_from.split("/") + date_to.split("/"):
    # 년도가 4글자인 경우 뒤의 두 글자만 추출
    if len(i) > 2:
      i = i[2:]
    # 두 자리 형식으로 변환
    hex_date += format(int(i), '02x')
  return hex_date

# LRC 계산하는 함수, 두 자리 형식으로 반환 -> ex)1이라면 01로 반환
# parameter: data=string
def cal_LRC(data):
  # 반환 변수
  LRC_val = 0
  
  # 하나씩 정수로 변환 -> EOR 계산
  for i in range(0, len(data), 2):
    LRC_val ^= int(data[i:i+2], 16)
  # 두 자리 형식으로 반환
  return format(LRC_val, '02x')

# 받은 데이터의 CMD값을 기준으로 DATA해석(주의: 보낸 메세지와 받은 메세지의 CMD는 일치하지 않을 수도 있다.)
# 16진수를 10진수와 아스키코드로 변환한다. 자세한 내용은 pdf참조
# 오류가 발생 가능성이 있으므로 try를 사용하여 코드를 작성하였다.
# CMD = 2A
def decode_CMD_2A(data):
  try:
    print("--DISPLAY Borad Version: ", bytes([int(x, 16) for x in data[:20]]).decode('ascii', errors="ignore"))
    print("--SENSOR Board Version: ", bytes([int(x, 16) for x in data[20:40]]).decode('ascii', errors="ignore"))
    print("--IO Board Version: ", bytes([int(x, 16) for x in data[40:60]]).decode('ascii', errors="ignore"))
  except ValueError as e:
    print("오류발생: 데이터 길이가 충분하지 않습니다.")
  
# CMD = 32
def decode_CMD_32(data):
  try:
    print("--PRODUCT NUMBER: ", int(data[0], 16))
    print("--PRODUCT NAME: ", bytes([int(x, 16) for x in data[1:21]]).decode('ascii', errors="ignore"))
    print("--CH1 Gain: ", int(data[21], 16))
    print("--CH2 Gain: ", int(data[22], 16))
    print("--Max DETECTION LEVEL: ", int.from_bytes(bytes.fromhex(''.join(data[23:25])), byteorder='big'))
    print("--Min DETECTION LEVEL: ", int.from_bytes(bytes.fromhex(''.join(data[25:27])), byteorder='big'))
    print("--DOUBLE ENTRY PERCEPTION TIME: ", int.from_bytes(bytes.fromhex(''.join(data[27:29])), byteorder='big'))
    print("--PRODUCT PASSING TYPE: ", int(data[29], 16))
    print("--PASSING TIME: ", int.from_bytes(bytes.fromhex(''.join(data[30:32])), byteorder='big'))
    print("--DELAY TIME: ", int.from_bytes(bytes.fromhex(''.join(data[32:34])), byteorder='big'))
    print("--OPERATING TIME: ", int.from_bytes(bytes.fromhex(''.join(data[34:36])), byteorder='big'))
  except ValueError as e:
    print("오류발생: 데이터 길이가 충분하지 않습니다.")
  
# CMD = 35
def decode_CMD_35(data):
  try:
    print("--PRODUCT NUMBER: ", int(data[0], 16))
    print("--MACHINE STATUS: ", int(data[1], 16))
    print("--CH1 Peak: ", int.from_bytes(bytes.fromhex(''.join(data[2:4])), byteorder='big'))
    print("--CH2 Peak: ", int.from_bytes(bytes.fromhex(''.join(data[4:6])), byteorder='big'))
    print("--Max DETECTION LEVEL: ", int.from_bytes(bytes.fromhex(''.join(data[6:8])), byteorder='big'))
    print("--Min DETECTION LEVEL: ", int.from_bytes(bytes.fromhex(''.join(data[8:10])), byteorder='big'))
    print("--PRODUCTION Q'TY: ", int.from_bytes(bytes.fromhex(''.join(data[10:14])), byteorder='big'))
    print("--DETECION Q'TY: ", int.from_bytes(bytes.fromhex(''.join(data[14:16])), byteorder='big'))
  except ValueError as e:
    print("오류발생: 데이터 길이가 충분하지 않습니다.")
  
# CMD = 3A
## 내부 함수를 재귀적으로 호출하는 방식이 v6에서는 무의미하나 혹시 모를 오류가 발생했을 때를 대비하여 유지
def decode_CMD_3A(data):
  # Data Field 1 출력 68 byte
  def print_data_1(data):
    print("***************** DATA FIELD 1 *****************")
    print("--Sub command: ", int(data[0], 16))
    print("--Output method: ", int(data[1], 16))
      ## 년도는 2000년대 이후라고 가정, 출력형식은 (년/월/일 ~ 년/월/일)
    print("--Checking Period: ", 
        "20" + format(int(data[2], 16), '02d') + "/" + format(int(data[3], 16), '02d') + "/" + format(int(data[4], 16), '02d') +
        " ~ " +
        "20" + format(int(data[5], 16), '02d') + "/" + format(int(data[6], 16), '02d') + "/" + format(int(data[7], 16), '02d'))
    ## 년도는 2000년대 이후라고 가정, 출력형식은 (년/월/일 시:분:초)
    print("--Output date and time: ", 
        "20" + format(int(data[8], 16), '02d') + "/" + format(int(data[9], 16), '02d') + "/" + format(int(data[10], 16), '02d') + " " +
        format(int(data[11], 16), '02d') + ":" + format(int(data[12], 16), '02d') + ":" + format(int(data[13], 16), '02d'))
    print("--Production Quantity: ", int.from_bytes(bytes.fromhex(''.join(data[14:18])), byteorder='big'))
    ## Detection quantity는 little endian 방식인 것으로 확인
    print("--Detection Quantity: ", int.from_bytes(bytes.fromhex(''.join(data[18:22])), byteorder='little'))
    print("--SN: ", bytes([int(x, 16) for x in data[22:38]]).decode('ascii', errors="ignore"))
    print("--DISPLAY Borad Version: ", bytes([int(x, 16) for x in data[38:48]]).decode('ascii', errors="ignore"))
    print("--Main Board Version: ", bytes([int(x, 16) for x in data[48:58]]).decode('ascii', errors="ignore"))
    print("--Reject Board Version: ", bytes([int(x, 16) for x in data[58:68]]).decode('ascii', errors="ignore"))
    print("************************************************")
    
  # Data Field 2 출력 8 byte
  def print_data_2(data):
    print("***************** DATA FIELD 2 *****************")
    print("--Sub command: ", int(data[0], 16))
    ## 년도는 2000년대 이후라고 가정, 출력형식은 (년/월/일)
    print("--Date: ", 
      "20" + format(int(data[1], 16), '02d') + "/" + format(int(data[2], 16), '02d') + "/" + format(int(data[3], 16), '02d'))
    ## Detection quantity는 little endian 방식인 것으로 확인
    print("--Detection quantity: ", int.from_bytes(bytes.fromhex(''.join(data[4:8])), byteorder='little'))
    print("************************************************")
    
  # Data Field 3 출력 17 byte
  def print_data_3(data):
    print("***************** DATA FIELD 3 *****************")
    print("--Sub command: ", int(data[0], 16))
    print("--LOG TYPE: ", int(data[1], 16))
    print("--PRODUCT NUMBER: ", int(data[2], 16))
    ## 년도는 2000년대 이후라고 가정, 출력형식은 (년/월/일 시:분:초)
    print("--DETECTING TIME: ", 
      "20" + format(int(data[3], 16), '02d') + "/" + format(int(data[4], 16), '02d') + "/" + format(int(data[5], 16), '02d') + " " +
      format(int(data[6], 16), '02d') + ":" + format(int(data[7], 16), '02d') + ":" + format(int(data[8], 16), '02d'))
    print("--DETECTING COUNT: ", int.from_bytes(bytes.fromhex(''.join(data[9:11])), byteorder='big'))
    print("--PRODUCT COUNT: ", int.from_bytes(bytes.fromhex(''.join(data[11:14])), byteorder='big'))
    print("--NULL: ", int.from_bytes(bytes.fromhex(''.join(data[14:17])), byteorder='big'))
    print("************************************************")
  
  try:
    # data가 비어 있는 경우 오류 처리
    if len(data) <= 0:
      raise ValueError("Data 길이가 충분하지 않습니다.")
    
    # Sub command가 1인경우 == Data Field 1(68 bytes)
    elif int(data[0], 16) == 1:
      print_data_1(data)
      data = data[68:]

    # Sub command가 2 인경우 == Data field 2(8 bytes)
    elif int(data[0], 16) == 2:
      print_data_2(data)
      data = data[8:]
      
    # Sub command가 3인 경우 == Data Filed 3 (17 bytes)
    elif int(data[0], 16) == 3:
      print_data_3(data)
      data = data[17:]

    # 일치하는 Sub command가 없는 경우
    else:
      raise ValueError("Sub command 오류")
  
  # 오류가 발생했을 경우 출력    
  except ValueError as e:
    print("오류발생: ", e)
    return None
  
  # 오류 검출 코드
  finally:
    # data가 남은 것을 출력하기 위한 코드
    print("--아직 출력하지 않은 data 길이(0이면 정상 작동): ", len(data))
    print("************************************************")
    
  
# 결과를 출력하는 함수
def print_result(rec_data):
  # 받은 DATA 출력(16진수)
  print("-----------------------------------------------------------DATA------------------------------------------------------------")
  print(rec_data)

  # 16진수를 ASCII로 변환
  print("-------------------------------------------------------16 to STRING--------------------------------------------------------")
  # ascii_string = ""
  # rec_data에서 ":" 제거
  only_hex_data = [i.replace(":", "") for i in rec_data]

  # 받은 데이터를 아스키코드 형식으로 출력
  rec = ""
  for i in only_hex_data[4:-1]:
    if i == "00":
      rec += " "
    rec += chr(int(i,16))
  print("RECEIVED: ", rec)

  # STX ETX 확인
  if only_hex_data[0] == "02":
    print("STX: 정상")
  else:
    print("STX: 오류")
  if only_hex_data[-2] == "03":
    print("ETX: 정상")
  else:
    print("ETX: 오류")

  # LENGTH 출력
  print("LENGTH: ", int.from_bytes(bytes.fromhex(''.join(only_hex_data[1:3])), byteorder='big'))

  # CMD별 DATA해석 및 출력
  print("CMD: ", only_hex_data[3])
  print("DATA:")     
  if only_hex_data[3] == "2A": decode_CMD_2A(only_hex_data[4:-2])
  elif only_hex_data[3] == "32": decode_CMD_32(only_hex_data[4:-2])
  elif only_hex_data[3] == "35": decode_CMD_35(only_hex_data[4:-2])
  elif only_hex_data[3] == "3A": decode_CMD_3A(only_hex_data[4:-2])
    
  # LRC 출력 및 수신 데이터의 LRC를 계산해서 일치 여부 확인
  ## 불일치시 정확한 정보가 전달되지 않았을 확률 존재
  print("LRC: ", only_hex_data[-1])
  calculated_LRC = cal_LRC(''.join(only_hex_data[:-1])).upper()
  if only_hex_data[-1] == calculated_LRC:
    print("LRC 일치 여부: O")
  else:
    print("LRC 일치 여부: X")
    # 계산된 LRC 출력
    print("cal_LRC: " + calculated_LRC)
  print("---------------------------------------------------------------------------------------------------------------------------")
  print("")
  print("")
  
# 소켓을 종료하는 함수
def terminate_socket(socket):
  print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  print("10초가 지나 소켓 연결을 종료합니다.")
  print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
  print("")
  socket.close()
  
  
######################################################################################################################################
######################################################################################################################################
# 소켓을 만든다.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  # connect함수로 접속을 한다.
  client_socket.connect((HOST, PORT))
  print("connected")
except Exception as e: 
    print("something's wrong with %s:%d. Exception is %s" % (HOST, PORT, e))
finally:
    # 메세지 입력 (실전용)
    ##################################################
    # send message
    # Frame format(STX, LENGTH, CMD, DATA, ETX, LRC), 16진수로 입력 ex)26 -> 1A로 입력
    STX = "02" # 1 byte, default
    ETX = "03" # 1 byte, default
    
    # 아래의 것들만 수정(나머지는 계산되거나 혹은 정해진 값)
    #################################################
    CMD = "3a" # 1 byte
    # CMD = 3A인 경우 날짜 계산
    ## 탐색 날짜 범위 <- 형식은 십진수로 년/월/일 <- xx/x/x ~ xxxx/xx/xx, 필요 숫자 갯수: 년=2,4, 월=1,2, 일=1,2 ex)20/1/1, 2020/01/01 <- 2020년 1월 1일
    date_from = "2024/1/1"
    date_to = "2024/1/19"
    #################################################
    
    # 아래는 v5에서 사용하지 않아서 임시 주석처리
    ## ***주의*** ex)2020/01/01, 2020/01/10 을 입력한 경우 date_between 값은 9이다. 따라서 총 10일을 검색하기 위해 + 1을 하였다.
    # date_format = "%Y/%m/%d"
    # date_between = abs((datetime.strptime(date_from, date_format) - datetime.strptime(date_to, date_format)).days) + 1
    # print(date_between)
    
    if CMD == "3a":
      DATA = cal_send_DATA_CMD_3A(date_from, date_to) # n byte
    # 나머지 경우 DATA 값 "N/A" (pdf 참조)
    else:
      DATA = ""
    
    LENGTH = format(len(DATA)//2+6, '04x') # 2 byte
    LRC = cal_LRC(STX+LENGTH+CMD+DATA+ETX) # 1 byte
    
    # 전송메세지 초기화 및 임시 변수 선언
    temp = (STX+LENGTH+CMD+DATA+ETX+LRC) # .upper()
    # \x00 형식의 byte로 변환 
    send_message = int(temp, 16).to_bytes(int(LENGTH, 16), byteorder="big")
    # 전송 메세지 확인차 출력  
    print(send_message)
    ##################################################
    
    # 위의 계산 무시하고 바로 메세지 입력하기(테스트용) <- 실제 기계와 통신할 경우에는 주석처리 바랍니다.
    ##################################################
    # send_message = "\x02\x00\x0c\x3A\x18\x01\x11\x18\x01\x11\x03\x37"
    # send_message = "\x02\x00\x0c\x3A\x18\x01\x11\x18\x01\x11\x03\x37"
    ##################################################
    
    # 이미 byte로 변환 되었기에 encode 불필요(encode 함수를 통한 byte 변환은 왠지 모르게 오류가 났었음)
    message = send_message#.encode();
    
    # 메시지 길이를 구한다.
    length = len(message);
    # server로 리틀 엔디언 형식으로 데이터 길이를 전송한다. -> big으로 수정
    # client_socket.sendall(length.to_bytes(4, byteorder="little"));
    
    # 10초 뒤에 통신 강제종료용 타이머
    timer  = threading.Timer(10, terminate_socket, [client_socket])
    timer.start()
    
    # message = codecs.encode(send_message)
    client_socket.sendall(message);
    print("client - send message : ", send_message);
    
    
    # 보내주는 대로 정보 받아오기
    try:
      while True:
        data = client_socket.recv(1024);
        # 더 이상 받는 데이터가 없다면 break
        if not data:
          break
      
        # msg = data.decode();
        print('Received from : ', data);

        # 변수 저장 - str->hex(list)
        rec_data = decode_string_to_hex(data)
        
        # 정보출력
        ## CMD가 3A인 경우에 슬라이싱하여 호출
        if rec_data[3] == '3A:':
          # 정보가 남아있다면 계속 진행
          while rec_data:
            # Data Field 1
            if int(rec_data[4][:2], 16) == 1:
              print_result(rec_data[:74])
              rec_data = rec_data[74:]
            # Data Field 2
            elif int(rec_data[4][:2], 16) == 2:
              print_result(rec_data[:14])
              rec_data = rec_data[14:]
            # Data Field 3
            elif int(rec_data[4][:2], 16) == 3:
              print_result(rec_data[:23])
              rec_data = rec_data[23:]
        ## 나머지 경우 출력
        else:
          print_result(rec_data)
    
    # 이러나 저러나 소켓 종료
    except:
      client_socket.close()    
    
    finally:
      client_socket.close()
