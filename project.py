import pymysql
import datetime
import sys
import time
import schedule
from apscheduler.schedulers.background import BackgroundScheduler
import threading


#변수 선언
conn, cursor = None, None # 각각 connect()를 받는 변수, cursor ()를 받는 변수



#실행부

# Python과 MySQL연동 (Workbench)  

def ConnectMySQL() :
    conn = pymysql.connect(
    host = 'localhost', 
    user = 'StudyManager', 
    password = 'study1234',
    db = 'StudyMember', 
    charset = 'utf8'
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return (conn,cursor)


# 휴대폰 번호 조회

def SearchPhoneNumber() :
    conn, cursor = ConnectMySQL()
    PhoneNumber = int(input("휴대폰 번호 뒤 8자리 : "))
    cursor.execute('USE StudyMember;')
    
    SearchPNumCommand = "SELECT * FROM Member WHERE M_PHONE = %s"
    
    with conn.cursor() as cur:
        cur.execute(SearchPNumCommand,PhoneNumber)
        SelectNum = cur.fetchall()
        IsThereAnyNum = bool(SelectNum)
        conn.commit()
        
    return (IsThereAnyNum, PhoneNumber)


# 입실 여부 조회

def CheckEnterRegister(PhoneNumber) :
    conn, cursor = ConnectMySQL()
    cursor.execute('USE StudyMember;')
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
            
        SelectDoorDataCommand = '''SELECT * FROM DOOR 
                                    WHERE  D_NUMBER = 
									                (SELECT S_NUMBER 
                                                    FROM MEMBER 
                                                    WHERE M_PHONE = %s)'''
        cur.execute(SelectDoorDataCommand,PhoneNumber)
        DoorData = cur.fetchall()
        if DoorData[0]["ENTER_TIME"] == None :
            return False
        elif DoorData[0]["LEAVE_TIME"] != None and DoorData[0]["ENTER_TIME"] < DoorData[0]["LEAVE_TIME"] :
            return False
        else : return True




# 스케쥴링 회원 삭제 후 좌석 비우기 함수, 하루에 1회 시행

def DeleteMem_ResetSeat () :
    conn, cursor = ConnectMySQL()
    cursor.execute('USE StudyMember;')
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        
        SearchEndSeatCommand ='''SELECT * FROM MEMBER,SEAT 
                                WHERE MEMBER.S_NUMBER = SEAT.S_NUMBER AND RENT_END < CURDATE()'''
        
        Search2WeekExcessCommand = '''SELECT * FROM MEMBER,DOOR 
                                    WHERE MEMBER.S_NUMBER = DOOR.D_NUMBER AND 
                                    DATE(LEAVE_TIME) < SUBDATE(CURDATE(), INTERVAL 14 DAY)'''
                                            
        cur.execute(SearchEndSeatCommand)
        EndSeatList = cur.fetchall() 
        cur.execute(Search2WeekExcessCommand)
        ExceDoorList = cur.fetchall()
        
        DeleteMemCommand = "DELETE FROM MEMBER WHERE M_PHONE = %s"
        
        ResetSeatCommand = '''UPDATE SEAT
                            SET RENT_START = NULL, RENT_END = NULL , RENT_PAYMENT = NULL
                            WHERE S_NUMBER = 
                                            (SELECT S_NUMBER
	                                        FROM   MEMBER
		                                    WHERE  M_PHONE = %s)''' 
        ResetDoorCommand ='''UPDATE DOOR
                            SET ENTER_TIME = NULL, LEAVE_TIME = NULL
                            WHERE D_NUMBER = 
                                            (SELECT S_NUMBER
	                                        FROM   MEMBER
		                                    WHERE  M_PHONE = %s)'''
        
         # 종료 기간이 지난 회원 정보 삭제
        
        for i in EndSeatList:
            cur.execute(DeleteMemCommand,i["M_PHONE"])
            cur.execute(ResetSeatCommand,i["M_PHONE"])
            cur.execute(ResetDoorCommand,i["M_PHONE"])
            conn.commit()
        
        for i in ExceDoorList:
            cur.execute(DeleteMemCommand,i["M_PHONE"])
            cur.execute(ResetSeatCommand,i["M_PHONE"])
            cur.execute(ResetDoorCommand,i["M_PHONE"])
            conn.commit()
        
        
            
            
# 스케쥴링 스터디룸 비우기 함수, 매분 01초 마다 실행

def ResetRoom () :
    
    conn, cursor = ConnectMySQL()
    cursor.execute('USE StudyMember;')
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        SearchRoomCommand = "SELECT ROOM.R_NUMBER, M_PHONE FROM ROOM, MEMBER WHERE ROOM.SER_END < SYSDATE()"    
        cur.execute(SearchRoomCommand)
        RoomExcessList = cur.fetchall()

        ResetMemCommand = "UPDATE MEMBER SET R_NUMBER = %s WHERE M_PHONE = %s"
        ResetRoomCommand = "UPDATE ROOM SET SER_START = NULL, SER_END = NULL, SER_TIME = NULL WHERE R_NUMBER = %s;"
        
        for i in RoomExcessList :
            cur.execute(ResetMemCommand,(None,i["M_PHONE"]))
            cur.execute(ResetRoomCommand,i["M_PHONE"])
            conn.commit()



# 스케쥴링 스터디룸 잔여시간 초기화 함수, 매주 월요일 00시 00분 01초마다 실행
  
def ResetSTime () :
    
    conn, cursor = ConnectMySQL()
    cursor.execute('USE StudyMember;')
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        
        ResetResTimeCommand = "UPDATE MEMBER SET SER_REMAINING = 20"
        
        cur.execute(ResetResTimeCommand)
        conn.commit()


# 함수 DeleteMem_ResetSeat, ResetRoom 스케줄링 




def Thread_function ():

    schedule.every().day.at("00:00:01").do(DeleteMem_ResetSeat)
    schedule.every().minute.at(":01").do(ResetRoom)
    schedule.every().monday.at("00:00:01").do(ResetSTime)
    
    while(True) :
        schedule.run_pending()
        time.sleep(1)

# 스레드모듈 를 통한 스케쥴링 함수와 메뉴 발생을 병렬처리

threadTool = threading.Thread(target = Thread_function)
threadTool.daemon = True
threadTool.start()






# 메뉴 1번. 회원가입 및 신규 좌석 대여 등록

def Op1_MemberRegister() : 
    conn, cursor = ConnectMySQL()
    
    cursor.execute('USE StudyMember;')
    cursor.execute('SELECT * FROM seat WHERE RENT_Start IS NULL ORDER BY S_Number')
    RemainedSeat = cursor.fetchall()
    IsThereAnyEmptySeat = bool(RemainedSeat)
    
    
    if IsThereAnyEmptySeat == False : # 비어있는 좌석이 없을 경우
        print('''죄송합니다. 비어있는 좌석이 없어 회원등록이 불가합니다. 
나중에 다시 방문해주시기 바랍니다. 감사합니다.\n\n
''')
        
    else : # 빈 좌석이 있을 경우 회원 등록
        print("현재 잔여 좌석이 "+str(len(RemainedSeat))+"개 남아 있습니다. 회원 등록을 진행합니다.")
        while(True) :
            PhoneNumber = int(input("신규가입자 휴대폰 번호 뒤 8자리 : "))
            if len(str(PhoneNumber)) == 8 : break
            print("[입력오류]: 등록을 위해서는 휴대폰 번호 뒤 8자리를 입력해주셔야합니다.")
            
        Name = input("신규가입자 이름 : ")
        Address = input("신규가입자 주소 : ")
        RestRoomTime = 20
        print('''\n====================================================
현재 남아 있는 좌석입니다. 1개월을 기준으로 결제하실수 있습니다.

큰 방의 좌석을 선택하실 경우 결제요금은 160,000원,
작은 방의 좌석을 선택하실 경우 결제요금은 150,000원 입니다.
결제 후, 기본적으로 1개월 마다 20시간의 스터디룸 이용권을 드립니다. 

원하시는 좌석을 선택해주세요. 
====================================================\n''')
        while(True) :
            for i in RemainedSeat:
                print(str(i["S_NUMBER"])+"번 좌석, 방 유형 : " + i["S_TYPE"] + " 이용요금 : " + str(i["S_CHARGE"]))
            print("\n")
            SelectSeatNum = int(input("신규 등록할 좌석 번호 : "))
            if SelectSeatNum in [i["S_NUMBER"] for i in RemainedSeat] : break
            print("\n[입력오류]: 잘못 누르셨습니다. 메뉴에 있는 좌석번호만을 선택해주세요.\n")
        
        print('''\n====================================================
선택한 좌석에 대한 결제일과 시작일을 년월일 기준으로 8글자를 입력해주세요.
====================================================\n''')
        while (True) :
             # 결제일 등록, 결제일의 경우 자동으로 현재시각에 맞춤
            PaymentDate = datetime.datetime.today().strftime("%Y%m%d")
    
            while(True) : #시작일 등록
                StartDate = input("시작일 8글자 ex) 20100101 :")
                if len(StartDate) == 8: break
                print("[입력오류]: 시작일 등록을 위해서는 년월일 8글자를 입력해주셔야 합니다.")
            while(True) :
                if int(PaymentDate) <= int(StartDate) : break
                print("[입력오류]: 시작일이 결제일보다 이를수는 없습니다. 다시 입력해주세요.\n")
            try:
                datetime.datetime(int(StartDate[0:4]),int(StartDate[4:6]),int(StartDate[6:8]))
                break
            except ValueError: 
                print("\n[입력오류]: 시작일 날짜를 잘못 입력하였습니다. 다시 입력해주세요.\n")
                continue
            
        TransPD = PaymentDate[0:4] +"-" + PaymentDate[4:6] + "-" + PaymentDate[6:8]
        TransSD = StartDate[0:4] + "-" + StartDate[4:6] + "-" + StartDate[6:8] 
        
        # EndDate 계산
        EndDate = datetime.datetime.strptime(StartDate,'%Y%m%d') + datetime.timedelta(days = 30)
        TransED = EndDate.isoformat()[:10]
        
        
        # MySQL에 반영
        print("\n회원을 등록합니다.\n")
        INSERTMemberCommand = "INSERT INTO MEMBER(M_PHONE, M_NAME, M_ADDRESS, SER_REMAINING,S_NUMBER,R_NUMBER) VALUES (%s, %s, %s, %s, %s, %s)" 
        UPDATESeatCommand = "UPDATE SEAT SET RENT_START = %s, RENT_END = %s, RENT_PAYMENT = %s WHERE S_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
        
        with conn.cursor() as cur:
            cur.execute(INSERTMemberCommand,(PhoneNumber,Name,Address,RestRoomTime,SelectSeatNum,None))
            cur.execute(UPDATESeatCommand,(TransSD,TransED,TransPD,PhoneNumber))
            conn.commit()
            print('''\n===============================
회원 등록이 완료되었습니다.
===============================\n''')
            time.sleep(2)




# 메뉴 2번. 입실 등록

def Op2_EnterRegister() :
    conn, cursor = ConnectMySQL()
    
    print('''====================================================
입실 등록절차를 시작합니다.
휴대폰 번호를 입력해주세요.
====================================================''')

    IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
        
    if IsThereAnyNum == False:
        print('''회원 등록이 되어있지 않습니다.
입실하려면 먼저 회원등록을 하셔야합니다.''')
        
    #### 시작일과 입실일 비교하는 과정추가가 필요함
    
    CheckEnterFinished = not CheckEnterRegister(PhoneNumber)    
    
    if CheckEnterFinished == False :
        print("\n입실등록이 이미 완료된 상황입니다.\n")
        time.sleep(2)
    else:
        with conn.cursor() as cur:
            EnterRegisterCommand = "UPDATE DOOR SET ENTER_TIME = SYSDATE() WHERE D_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
            cur.execute(EnterRegisterCommand,PhoneNumber)
            conn.commit()
        print("\n입실 등록이 완료되었습니다.\n")
        time.sleep(2)





# 메뉴 3번. 스터디룸 이용 등록
 
def Op3_StudyRoomRegister() :
    conn, cursor = ConnectMySQL()
    
    cursor.execute('USE StudyMember;')
    
    SearchRestRoomCommand = "SELECT * FROM ROOM WHERE SER_START IS NULL"
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(SearchRestRoomCommand)
        RestRoom = cur.fetchall()
        
        # 스터디룸 잔여 여부 현황 파악
        IsThereAnyRestRoom = bool(RestRoom)
        
        if IsThereAnyRestRoom == False :
            print("\n현재 모든 스터디룸이 사용중입니다. 나중에 다시 이용해주시기 바랍니다.")
        else :
            print('''====================================================
스터디룸 이용 등록절차를 시작합니다.
====================================================\n''')
            print("현재 이용가능한 스터디룸 목록입니다.\n")
            
            while(True) :
                ForOutWhile = 0
                for i in RestRoom:
                    print(str(i["R_NUMBER"])+"번 스터디룸, 스터디룸 최대 인원 : " + str(i["R_MAX"] ))
                print("\n")
            
            # 이용할 스터디룸 입력
                
                SelectRoomNum = int(input("신규 이용 등록할 스터디룸 번호 : "))
                for i in RestRoom:
                    if i["R_NUMBER"] == SelectRoomNum :
                        SelectedRoom = i
                        ForOutWhile = 1
                    
                if ForOutWhile == 1 : break 
                print("\n[입력오류]: 잘못 누르셨습니다. 메뉴에 있는 스터디룸 번호만을 선택해주세요.\n")
            
            # 선택한 스터디룸을 이용할 인원수 입력
            
            while(True) :
                PeopleNum = int(input('''총 몇 명이 이용하실 지 선택해주세요.\n
(※ 참고 : 인원 수는 스터디룸 최대 인원 수를 넘으면 안되며 최소 2명 이상이어야 합니다.)\n
이용인원 수 : '''))
                if PeopleNum <= 1 or PeopleNum > SelectedRoom["R_MAX"] :
                    print('''\n해당 스터디룸을 이용하기엔 적절하지 않은 이용 수 입니다.
다시 입력하고 싶으시면 아무키를 누르시고, 처음 메뉴로 돌아가고 싶으시면 1번을 눌러주세요.\n''')
                    SelectButton = input("입력: ")
                    if SelectButton == '1' :
                        conn.commit()
                        return
                    else : continue
                else : break
                
            # 사람 명 수 만큼 휴대폰 번호 입력 
            for i in range(PeopleNum) : 
                while(True):
                    print("휴대폰 번호 뒤 8자리를 입력해주세요.")
                    IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
                    if IsThereAnyNum == False: # 휴대폰 번호가 등록되어 있지 않을 경우
                        print('''해당 휴대폰 번호는 회원 명단에 없습니다.
다시 입력하고 싶으시면 아무키를 누르시고, 메뉴로 돌아가 회원가입을 원하시면 1번을 눌러주세요.\n''')      
                        SelectButton = input("입력: ")
                        if SelectButton == '1' :
                            conn.commit()
                            return
                        else : continue
                    else : # 먼저 입실을 하지 않았을 경우
                        CheckEnterFinished = CheckEnterRegister(PhoneNumber)
                        if CheckEnterFinished == False :
                            print("\n 해당 회원은 스터디룸 등록전 먼저 입실을 완료해주셔야 합니다. 메뉴로 돌아갑니다.\n")
                            time.sleep(3)
                            return
                        else : break
                RegisterRoomCommand = "UPDATE MEMBER SET MEMBER.R_NUMBER = %s WHERE M_PHONE = %s"
                cur.execute(RegisterRoomCommand,(SelectRoomNum,PhoneNumber))
                conn.commit()
            
              
                # 이용 시간 입력, 이용 시간은 시간 단위이며, 이용자 모두 남은 잔여시간이 이용시간 보다 같거나 커야 한다.
            while(True) :
                print("이용 시간을 입력합니다. 시간 단위로 입력가능합니다.")      
                TimeOfUse = int(input("이용 시간 입력 : "))
                RestTimeList = []
                SelectRestTimeCommand = "SELECT SER_REMAINING FROM MEMBER, ROOM WHERE MEMBER.R_NUMBER = ROOM.R_NUMBER"
                cur.execute(SelectRestTimeCommand)
                Resttime = cur.fetchall()
                for i in range(PeopleNum) : 
                    RestTimeList.append(Resttime[i]["SER_REMAINING"])
                    RestTimeList[i] = RestTimeList[i] - TimeOfUse
                if min(RestTimeList) < 0: 
                    print("회원 중 이용시간에 비해 잔여시간이 부족한 회원이 있습니다. 다시 입력해주세요.\n")
                else : break
            
                            # 시작 시간은 스터디룸 등록을 시도하는 현재 시각에 맞추어 자동으로 분 단위까지 입력
            
            print("\n이용시작 시간이 설정되었습니다. 이용 시작 시간은 현재시각을 기준으로 등록됩니다.\n")
            StartTime = datetime.datetime.today().strftime("%Y%m%d%H%M")
                
            
             
            # 해당 회원들의 시작시간, 종료시간 파악
            
            EndTime = datetime.datetime.strptime(StartTime,'%Y%m%d%H%M') + datetime.timedelta(hours = TimeOfUse)
            StartTime = datetime.datetime.strptime(StartTime,'%Y%m%d%H%M')
            
            # 시작시간, 종료시간 문자열로 변형
            
            TransST = StartTime.strftime('%Y-%m-%d %H:%M:%S') 
            TransET = EndTime.strftime('%Y-%m-%d %H:%M:%S')
            
            # 시간 등록 명령 실행
            RegisterTimeCommand = "UPDATE ROOM SET SER_START = %s, SER_END = %s , SER_TIME = %s WHERE R_NUMBER = %s"
            cur.execute(RegisterTimeCommand,(TransST,TransET,TimeOfUse,SelectRoomNum))
            conn.commit()
            
            #이용자들의 잔여시간 차감 명령 실행
            SubRestTimeCommand = "UPDATE MEMBER SET SER_REMAINING = SER_REMAINING - %s WHERE R_NUMBER = %s"
            cur.execute(SubRestTimeCommand,(TimeOfUse,SelectRoomNum))
            conn.commit()
            print('''\n===============================
스터디룸 등록이 완료되었습니다.
===============================\n''')
            time.sleep(2)



# 메뉴 4번. 기존 이용 회원의 좌석변경

def Op4_ChangeSeatNum() :
    conn, cursor = ConnectMySQL()
    cursor.execute('USE StudyMember;')
    
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        print('''====================================================
좌석 변경가능 여부를 확인하기 위해
휴대폰 번호를 입력해주세요.
====================================================''')
        IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
        if IsThereAnyNum == False :
            print('''잘못 입력하셨거나 회원 등록이 되어있지 않습니다.
 메뉴로 돌아갑니다.\n''')
        else :
            CheckEnterFinished = CheckEnterRegister(PhoneNumber)
            if CheckEnterFinished == False :
                print("\n 좌석변경전 먼저 입실등록을 해주셔야 합니다. 메뉴로 돌아갑니다. \n")
                return
            
            SearchSeatCommand = '''SELECT * FROM seat WHERE RENT_Start IS NULL and S_TYPE = 
                                (SELECT seat.S_TYPE FROM seat, member 
                                WHERE seat.s_number = member.s_number and member.m_phone = %s) 
                                ORDER BY S_Number'''
            cur.execute(SearchSeatCommand,PhoneNumber)
            RemainedSeat = cur.fetchall()
            IsThereAnySeat = bool(RemainedSeat)
            
            if IsThereAnySeat == False :
                
                print("\n죄송합니다. 현재 잔여 좌석이 없어 좌석변경이 불가능합니다.\n")
            else :
                print('''\n==========================
좌석 변경을 시작합니다.
==========================\n''')
                print("현재 변경가능한 좌석 목록입니다.\n")
                for i in RemainedSeat :
                    print("좌석번호 : " + str(i["S_NUMBER"])+ "번 좌석")
                print("\n 원하시는 좌석을 선택해주세요.\n")
                while True :
                    SelectSeatNum = input("좌석 번호 : ")
                    if SelectSeatNum in [str(i["S_NUMBER"]) for i in RemainedSeat] : break
                    print("목록에 나와있는 좌석만 선택해주세요.\n") 
                
                MySeatDataCommand = '''SELECT * FROM SEAT WHERE S_NUMBER =
							        (SELECT S_NUMBER
                                    FROM MEMBER
                                    WHERE M_PHONE = %s)'''
                
                MyDoorDataCommand = '''SELECT * FROM DOOR WHERE D_NUMBER =
							        (SELECT S_NUMBER
                                    FROM MEMBER
                                    WHERE M_PHONE = %s)'''
                
                
                cur.execute(MySeatDataCommand,PhoneNumber)
                SeatData = cur.fetchall()
                cur.execute(MyDoorDataCommand,PhoneNumber)
                DoorData = cur.fetchall()
                
                UpDateSeatCommand = ''' UPDATE SEAT
                                        SET RENT_START = %s , RENT_END = %s , RENT_PAYMENT = %s
                                        WHERE S_NUMBER = 
                                                    (SELECT S_NUMBER
	                                                FROM   MEMBER
		                                            WHERE  M_PHONE = %s)'''
                
                ChangeSeatCommand = "UPDATE MEMBER SET MEMBER.S_NUMBER = %s WHERE M_PHONE = %s"
                
                UpDateDoorCommand = '''UPDATE DOOR 
                                       SET ENTER_TIME = %s , LEAVE_TIME = %s 
							           WHERE D_NUMBER = 
											            (SELECT S_NUMBER
											            FROM   MEMBER
											            WHERE  M_PHONE = %s)'''
                
                
                cur.execute(UpDateSeatCommand,(None,None,None,PhoneNumber))
                cur.execute(UpDateDoorCommand,(None,None,PhoneNumber))
                cur.execute(ChangeSeatCommand,(int(SelectSeatNum),PhoneNumber))
                cur.execute(UpDateSeatCommand,(SeatData[0]["RENT_START"],SeatData[0]["RENT_END"],SeatData[0]["RENT_PAYMENT"],PhoneNumber))
                cur.execute(UpDateDoorCommand,(DoorData[0]["ENTER_TIME"],DoorData[0]["LEAVE_TIME"],PhoneNumber))
                conn.commit()
                print('''============================
좌석 변경이 완료되었습니다.
============================\n''')
                time.sleep(2)






# 메뉴 5번. 좌석 대여 연장

def Op5_ExtendSeatDate () :
    conn, cursor = ConnectMySQL()
    
    cursor.execute('USE StudyMember;')
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        print('''====================================
좌석연장 절차를 시작합니다.
연장은 30일 단위로 갱신할수 있습니다.
휴대폰번호 뒤 8자리를 입력해주세요.
====================================\n''')
        IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
        if IsThereAnyNum == False :
            print('''잘못 입력하셨거나 회원 등록이 되어있지 않습니다.
 메뉴로 돌아갑니다.\n''')
        else :
            MySeatDataCommand = '''SELECT * FROM SEAT WHERE S_NUMBER =
							        (SELECT S_NUMBER
                                    FROM MEMBER
                                    WHERE M_PHONE = %s)'''
                
            cur.execute(MySeatDataCommand,PhoneNumber)
            SeatData = cur.fetchall()
            AfterExtendTime = SeatData[0]["RENT_END"] + datetime.timedelta(days = 30)
            SeatData[0]["RENT_END"] = AfterExtendTime.strftime('%Y-%m-%d')
            
            UpDateSeatCommand = ''' UPDATE SEAT
                                    SET RENT_END = %s
                                    WHERE S_NUMBER = 
                                                    (SELECT S_NUMBER
	                                                FROM   MEMBER
		                                            WHERE  M_PHONE = %s)'''
            cur.execute(UpDateSeatCommand,(SeatData[0]["RENT_END"],PhoneNumber))            
            conn.commit()
            print('''============================
좌석 연장이 완료되었습니다.
============================\n''')
            time.sleep(2)


# 메뉴 6번. 퇴실 등록

def Op6_ExitRegister () :
    conn, cursor = ConnectMySQL()
    
    print('''====================================================
퇴실 등록절차를 시작합니다.
휴대폰 번호를 입력해주세요.
====================================================''')

    IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
        
    if IsThereAnyNum == False:
        print('''회원 등록이 되어있지 않습니다.
퇴실하려면 먼저 회원등록을 하셔야합니다.\n''')
        
    else :
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            
            CheckEnterFinished = CheckEnterRegister(PhoneNumber)
            
            if CheckEnterFinished == False : print("\n퇴실을 하시려면 먼저 입실을 해주셔야 합니다.")

            else :
                EnterRegisterCommand = "UPDATE DOOR SET LEAVE_TIME = SYSDATE() WHERE D_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
                cur.execute(EnterRegisterCommand,PhoneNumber)
                conn.commit()
                print("\n퇴실 등록이 완료되었습니다.\n")
                time.sleep(2)




# 메뉴 7번. 메뉴 종료

def Op7_ExitMenu() :
    
    print("\n메뉴 프로그램을 완전히 종료합니다.\n")
    sys.exit()



# 전체 메뉴 리스트 불러오기

def MenuList() :
    MENU = '''====================================================
StudyMember 독서실에 오신 것을 환영합니다.

다음 중 메뉴를 선택해주세요. 

※ 참고 ※
1. 처음 오신 분이라면 회원가입 및 신규 좌석 대여 등록 후 입실이 가능합니다.
2. 입실 등록 완료 후 스터디룸 등록, 좌석 대여 / 변경, 퇴실이 가능합니다.

''' 

    print(MENU)
    SelectedButtion = int(input(''' ======== 메뉴 항목 =======

1. 회원가입 및 신규 좌석 대여 등록 
2. 입실 등록 
3. 스터디룸 이용 등록 
4. 기존 좌석 변경
5. 좌석 대여 연장 
6. 퇴실 등록
7. 메뉴 종료 

원하시는 항목을 선택해주세요: '''))
    
    if SelectedButtion == 1:
        
        Op1_MemberRegister() # 등록절차 수행
        
    elif SelectedButtion == 2:
        
        Op2_EnterRegister() # 입실 절차 수행
         
    elif SelectedButtion == 3:
        
        Op3_StudyRoomRegister() # 스터디룸 이용 등록 절차 수행
        
    elif SelectedButtion == 4:
        
        Op4_ChangeSeatNum() # 좌석 변경 수행
         
    elif SelectedButtion == 5:
        
        Op5_ExtendSeatDate() # 좌석 대여 연장 수행
         
    elif SelectedButtion == 6:
        
        Op6_ExitRegister () # 퇴실 절차 수행
        
    elif SelectedButtion == 7:
        
        Op7_ExitMenu() # 메뉴 종료 절차 수행
                
    else :
        print('''\n****************************************************
누르신 항목이 메뉴에 없습니다. 다시 입력해주세요.
****************************************************\n''') 
        MenuList()
    
    

while(True) : MenuList()

