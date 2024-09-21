# 기계에서 정보를 받아오면 그 정보를 \x00 형식으로 바꾸어서 socketServer 코드에 넣고 바로 시험해보고자 만든 코드

# 클립보드 복사 기능
import pyperclip

# 변환할 기계에서 수신한 정보
machine_data = "02: 00: 4A: 3A: 01: 00: 18: 01: 01: 18: 01: 13: 18: 01: 13: 0F: 0B: 1A: 00: 00: 00: 2B: 01: 00: 00: 00: 32: 33: 31: 31: 31: 36: 32: 35: 52: 30: 00: 00: 00: 00: 00: 00: 56: 2E: 32: 30: 31: 30: 32: 32: 61: 00: 56: 2E: 32: 30: 30: 31: 30: 39: 61: 00: 56: 2E: 31: 39: 30: 31: 30: 33: 61: 00: 03: 25: 02: 00: 0E: 3A: 02: 18: 01: 10: 01: 00: 00: 00: 03: 3F: 02: 00: 17: 3A: 03: 02: 01: 18: 01: 10: 09: 1B: 2B: 00: 01: 00: 00: 0A: FF: FF: FF: 03: E8: 02: 00: 17: 3A: 03: 00: 01: 18: 01: 10: 09: 1F: 07: 00: 02: 00: 00: 15: FF: FF: FF: 03: DE: 02: 00: 17: 3A: 03: 02: 01: 18: 01: 10: 0F: 37: 05: 00: 02: 00: 00: 18: FF: FF: FF: 03: FD: "


result = "\\x"

for idx, word in enumerate(machine_data):
    if(idx%4==0 or idx%4==1):
        result += word
    elif(idx%4==2):
        result += "\\x"

pyperclip.copy(result[:-2])
print(result[:-2])

# 3A 형식으로 출력까지 하고 싶을 때
def decode_CMD_3A(data):
    try:
        # data가 비어 있는 경우 오류 처리
        if len(data) <= 0:
            raise ValueError("Data 길이가 충분하지 않습니다.")
    
        # Sub command가 1인경우 == Data Field 1(68 bytes)
        elif int(data[0], 16) == 1:
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
            ## 남은 정보있는지 확인을 위한 도려내기 (68 bytes)
            data = data[68:]

            # Sub command가 2 인경우 == Data field 2(8 bytes)
        elif int(data[0], 16) == 2:
            # DATA FIELD 2(8 bytes)
            print("***************** DATA FIELD 2 *****************")
            print("--Sub command: ", int(data[0], 16))
            ## 년도는 2000년대 이후라고 가정, 출력형식은 (년/월/일)
            print("--Date: ", 
                "20" + format(int(data[1], 16), '02d') + "/" + format(int(data[2], 16), '02d') + "/" + format(int(data[3], 16), '02d'))
                ## Detection quantity는 little endian 방식인 것으로 확인
            print("--Detection quantity: ", int.from_bytes(bytes.fromhex(''.join(data[4:8])), byteorder='little'))
            print("************************************************")
            ## 남은 정보있는지 확인을 위한 도려내기 (8 bytes)
            data = data[8:]

            # Sub command가 3인 경우 == Data Filed 3 (17 bytes)
        elif int(data[0], 16) == 3:
            # DATA FIELD 3(17 bytes)
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
            ## 남은 정보있는지 확인을 위한 도려내기 (17 bytes)
            data = data[17:]

        # 일치하는 Sub command가 없는 경우
        else:
            raise ValueError("Sub command 오류")

    except ValueError as e:
        print("오류발생: ", e)
        return None
    # 오류 검출 코드
    finally:
        print("--아직 출력하지 않은 data 길이(0이면 정상 작동): ", len(data))
        print("************************************************")