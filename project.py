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


# 스케쥴링 회원 삭제 함수

# 스케쥴링 스터디룸 비우기 함수






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
        print("\n회원을 등록합니다.")
        INSERTMemberCommand = "INSERT INTO MEMBER(M_PHONE, M_NAME, M_ADDRESS, M_REST,S_NUMBER,R_NUMBER) VALUES (%s, %s, %s, %s, %s, %s)" 
        UPDATESeatCommand = "UPDATE SEAT SET S_START = %s, S_END = %s, S_PAYMENT = %s WHERE S_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
        
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
        
    #### 시작일과 입실일 비교하는 과정추가가 필요함    
        
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
                    break
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
                    if IsThereAnyNum == False:
                        print('''해당 휴대폰 번호는 회원 명단에 없습니다.
다시 입력하고 싶으시면 아무키를 누르시고, 메뉴로 돌아가 회원가입을 원하시면 1번을 눌러주세요.\n''')      
                        SelectButton = input("입력: ")
                        if SelectButton == '1' :
                            conn.commit()
                            return
                        else : continue
                    else : break
                RegisterRoomCommand = "UPDATE MEMBER SET MEMBER.R_NUMBER = %s WHERE M_PHONE = %s"
                cur.execute(RegisterRoomCommand,(SelectRoomNum,PhoneNumber))
                conn.commit()
            
              
                # 이용 시간 입력, 이용 시간은 시간 단위이며, 이용자 모두 남은 잔여시간이 이용시간 보다 같거나 커야 한다.
            while(True) :
                print("이용 시간을 입력합니다. 시간 단위로 입력가능합니다.")      
                TimeOfUse = int(input("이용 시간 입력 : "))
                RestTimeList = []
                SelectRestTimeCommand = "SELECT M_REST FROM MEMBER, ROOM WHERE MEMBER.R_NUMBER = ROOM.R_NUMBER"
                cur.execute(SelectRestTimeCommand)
                Resttime = cur.fetchall()
                for i in range(PeopleNum) : 
                    RestTimeList.append(Resttime[i]["M_REST"])
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
            RegisterTimeCommand = "UPDATE ROOM SET RES_START = %s, RES_END = %s , RES_TIME = %s WHERE R_NUMBER = %s"
            cur.execute(RegisterTimeCommand,(TransST,TransET,TimeOfUse,SelectRoomNum))
            conn.commit()
            
            #이용자들의 잔여시간 차감 명령 실행
            SubRestTimeCommand = "UPDATE MEMBER SET M_REST = M_REST - %s WHERE R_NUMBER = %s"
            cur.execute(SubRestTimeCommand,(TimeOfUse,SelectRoomNum))
            conn.commit()
            print('''\n===============================
스터디룸 등록이 완료되었습니다.
===============================\n''')
            



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
            SearchSeatCommand = '''SELECT * FROM seat WHERE S_Start IS NULL and S_TYPE = 
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
                
                cur.execute(MySeatDataCommand,PhoneNumber)
                SeatData = cur.fetchall()
                
                
                UpDateSeatCommand = ''' UPDATE SEAT
                                        SET S_START = %s , S_END = %s , S_PAYMENT = %s
                                        WHERE S_NUMBER = 
                                                    (SELECT S_NUMBER
	                                                FROM   MEMBER
		                                            WHERE  M_PHONE = %s)'''
                
                ChangeSeatCommand = "UPDATE MEMBER SET MEMBER.S_NUMBER = %s WHERE M_PHONE = %s"
                
                
                cur.execute(UpDateSeatCommand,(None,None,None,PhoneNumber))
                cur.execute(ChangeSeatCommand,(int(SelectSeatNum),PhoneNumber))
                cur.execute(UpDateSeatCommand,(SeatData[0]["S_START"],SeatData[0]["S_END"],SeatData[0]["S_PAYMENT"],PhoneNumber))
                conn.commit()
                print('''============================
좌석변경이 완료되었습니다.
============================\n''')
                    
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
        
        Op4_ChangeSeatNum() # 좌석 변경 수행
         
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
    
    


MenuList()









