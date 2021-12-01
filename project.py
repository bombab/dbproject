import pymysql
import datetime


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

# 메뉴 1번. 회원가입 및 신규 좌석 대여 등록

def Op1_MemberRegister() : 
    conn, cursor = ConnectMySQL()
    
    cursor.execute('USE StudyMember;')
    cursor.execute('SELECT * FROM seat WHERE S_Start IS NULL ORDER BY S_Number')
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
            while(True) :
                PaymentDate =  input("결제일 8글자 ex) 20100101 : ")
                if len(PaymentDate) == 8: break
                print("[입력오류]: 결제일 등록을 위해서는 년월일 8글자를 입력해주셔야 합니다.")
            while(True) :
                StartDate = input("시작일 8글자 ex) 20100101 :")
                if len(StartDate) == 8: break
                print("[입력오류]: 시작일 등록을 위해서는 년월일 8글자를 입력해주셔야 합니다.")
            while(True) :
                if int(PaymentDate) <= int(StartDate) : break
                print("[입력오류]: 시작일이 결제일보다 이를수는 없습니다. 다시 입력해주세요.\n")
            try:
                datetime.datetime(int(PaymentDate[0:4]),int(PaymentDate[4:6]),int(PaymentDate[6:8]))
                datetime.datetime(int(StartDate[0:4]),int(StartDate[4:6]),int(StartDate[6:8]))
                break
            except ValueError: 
                print("\n[입력오류]: 결제 날짜 혹은 시작일 날짜를 잘못 입력하였습니다. 다시 입력해주세요.\n")
                continue
            
        TransPD = PaymentDate[0:4] +"-" + PaymentDate[4:6] + "-" + PaymentDate[6:8]
        TransSD = StartDate[0:4] + "-" + StartDate[4:6] + "-" + StartDate[6:8] 
        
        # EndDate 계산
        EndDate = datetime.datetime(int(StartDate[0:4]),int(StartDate[4:6]),int(StartDate[6:8])) + datetime.timedelta(days = 30)
        TransED = str(EndDate.year) + "-" + str(EndDate.month) + "-" + str(EndDate.day)
        
        # MySQL에 반영
        print("\n회원을 등록합니다.")
        INSERTMemberCommand = "INSERT INTO MEMBER(M_PHONE, M_NAME, M_ADDRESS, M_REST,S_NUMBER,R_NUMBER) VALUES (%s, %s, %s, %s, %s, %s)" 
        UPDATESeatCommand = "UPDATE SEAT SET S_START = %s, S_END = %s, S_PAYMENT = %s WHERE S_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
        with conn:
            with conn.cursor() as cur:
                cur.execute(INSERTMemberCommand,(PhoneNumber,Name,Address,RestRoomTime,SelectSeatNum,None))
                cur.execute(UPDATESeatCommand,(TransSD,TransED,TransPD,PhoneNumber))
                conn.commit()
            


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
    else:
        with conn.cursor() as cur:
            EnterRegisterCommand = "UPDATE DOOR SET D_ENTER = SYSDATE() WHERE D_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
            cur.execute(EnterRegisterCommand,PhoneNumber)
            conn.commit()
        print("\n입실 등록이 완료되었습니다.\n")



# 메뉴 3번. 스터디룸 이용 등록
 
def Op3_StudyRoomRegister() :
    conn, cursor = ConnectMySQL()
    
    cursor.execute('USE StudyMember;')
    
    SearchRestRoomCommand = "SELECT * FROM ROOM WHERE RES_START IS NULL"
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
                for i in RestRoom:
                    print(str(i["R_NUMBER"])+"번 스터디룸, 스터디룸 최대 인원 : " + str(i["R_MAX"] ))
                print("\n")
            
            # 이용할 스터디룸 입력
                
                SelectRoomNum = int(input("신규 이용 등록할 스터디룸 번호 : "))
                if SelectRoomNum in [i["R_NUMBER"] for i in RestRoom] : break
                print("\n[입력오류]: 잘못 누르셨습니다. 메뉴에 있는 스터디룸 번호만을 선택해주세요.\n")
            
            # 선택한 스터디룸을 이용할 인원수 입력
            
            while(True) :
                PeopleNum = int(input('''총 몇 명이 이용하실 지 선택해주세요.\n
(※ 참고 : 인원 수는 스터디룸 최대 인원 수를 넘으면 안되며 최소 2명 이상이어야 합니다.)\n
이용인원 수 : '''))
                if PeopleNum <= 1 or PeopleNum > RestRoom[SelectRoomNum-1]["R_MAX"] :
                    print('''\n해당 스터디룸을 이용하기엔 적절하지 않은 이용 수 입니다.
다시 입력하고 싶으시면 아무키를 누르시고, 처음 메뉴로 돌아가고 싶으시면 1번을 눌러주세요.\n''')
                    SelectButton = int(input("입력: "))
                    if SelectButton == 1 :
                        conn.commit()
                        return
                    else : continue
                else : break
                
            # 사람 명 수 만큼 휴대폰 번호 입력 
            for i in range(PeopleNum) : 
                while(True):
                    print("휴대폰 번호 뒤 8자리를 입력해주세요.")
                    IsThereAnyNum, PhoneNumber = SearchPhoneNumber()
                    if IsThereAnyNum == False:
                        print('''해당 휴대폰 번호는 회원 명단에 없습니다.
다시 입력하고 싶으시면 아무키를 누르시고, 메뉴로 돌아가 회원가입을 원하시면 1번을 눌러주세요.\n''')      
                        SelectButton = int(input("입력: "))
                        if SelectButton == 1 :
                            conn.commit()
                            return
                        else : continue
                    else : break
                RegisterRoomCommand = "UPDATE MEMBER SET MEMBER.R_NUMBER = %d WHERE M_PHONE = %d"
                cur.execute(RegisterRoomCommand,(SelectRoomNum,PhoneNumber))
            
            # 이용 시간 입력, 시작시간은 정각이어야 하며 시간 단위로 입력해야한다.
            while (True) :
                while(True) :
                    StartYear,Month,Day,Hour =  input("이용시작 시간 년/월/일/시간 콤마 단위로 10글자 ex) 2010,01,01,17 : ").spilt(',')
                    if len(RoomStartTime) == 10: break
                    print("[입력오류]: 결제일 등록을 위해서는 년/월/일/시간 10글자를 입력해주셔야 합니다.")
                
                while(True) :
                    if int(PaymentDate) <= int(StartDate) : break
                    print("[입력오류]: 시작일이 결제일보다 이를수는 없습니다. 다시 입력해주세요.\n")
                try:
                    datetime.datetime(int(PaymentDate[0:4]),int(PaymentDate[4:6]),int(PaymentDate[6:8]))
                    datetime.datetime(int(StartDate[0:4]),int(StartDate[4:6]),int(StartDate[6:8]))
                    break
                except ValueError: 
                    print("\n[입력오류]: 결제 날짜 혹은 시작일 날짜를 잘못 입력하였습니다. 다시 입력해주세요.\n")
                    continue 
            
            RegisterTimeCommand = ""
            
            
        conn.commit()


##INSERT INTO SEAT VALUES(6,'작은방',150000,'2021-11-11','2021-12-10','2021-11-11');
##INSERT INTO MEMBER VALUES (87651346,'이름','주소',20,좌석번호,NULL);


# 메뉴 7번. 메뉴 종료

def Op7_ExitMenu() :
    print("\n메뉴를 나갑니다.\n") 


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
        
        Op2_EnterRegister() # 입실절차 수행
         
    elif SelectedButtion == 3:
        
        Op3_StudyRoomRegister() # 스터디룸 이용 등록 절차 수행
        
    elif SelectedButtion == 4:
        pass 
    elif SelectedButtion == 5:
        pass 
    elif SelectedButtion == 6:
        pass
    elif SelectedButtion == 7:
        
        Op7_ExitMenu() # 메뉴 종료 절차 수행
              
    else :
        print('''\n****************************************************
누르신 항목이 메뉴에 없습니다. 다시 입력해주세요.
****************************************************\n''') 
        MenuList()
    
    

while(True):
    MenuList()









