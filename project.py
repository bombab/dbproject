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



# 메뉴 1번 회원가입

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
        
    elif IsThereAnyEmptySeat == True : # 빈 좌석이 있을 경우 회원 등록
        print("현재 잔여 좌석이 "+str(len(RemainedSeat))+"개 남아 있습니다. 회원 등록을 진행합니다.")
        while(True) :
            PhoneNumber = int(input("신규가입자 휴대폰 번호 : "))
            if len(str(PhoneNumber)) == 8 : break
            print("[입력오류]: 등록을 위해서는 휴대폰 번호 8자리를 입력해주셔야합니다.")
            
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
                print("결제 날짜 혹은 시작일 날짜를 잘못 입력하였습니다. 다시 입력해주세요")
                continue
            
        TransPD = PaymentDate[0:4] +"-" + PaymentDate[4:6] + "-" + PaymentDate[6:8]
        TransSD = StartDate[0:4] + "-" + StartDate[4:6] + "-" + StartDate[6:8] 
        
        # EndDate 계산
        EndDate = datetime.datetime(int(StartDate[0:4]),int(StartDate[4:6]),int(StartDate[6:8])) + datetime.timedelta(days = 30)
        TransED = str(EndDate.year) + "-" + str(EndDate.month) + "-" + str(EndDate.day)
        
        print("\n회원을 등록합니다.")
        INSERTMemberCommand = "INSERT INTO MEMBER(M_PHONE, M_NAME, M_ADDRESS, M_REST,S_NUMBER,R_NUMBER) VALUES (%s, %s, %s, %s, %s, %s)" 
        UPDATESeatCommand = "UPDATE SEAT SET S_START = %s, S_END = %s, S_PAYMENT = %s WHERE S_NUMBER = (SELECT S_NUMBER FROM MEMBER WHERE M_PHONE = %s)"
        with conn:
            with conn.cursor() as cur:
                cur.execute(INSERTMemberCommand,(PhoneNumber,Name,Address,RestRoomTime,SelectSeatNum,None))
                cur.execute(UPDATESeatCommand,(TransSD,TransED,TransPD,PhoneNumber))
                conn.commit()
            

##INSERT INTO SEAT VALUES(6,'작은방',150000,'2021-11-11','2021-12-10','2021-11-11');
##INSERT INTO MEMBER VALUES (87651346,'이름','주소',20,좌석번호,NULL);


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
        
        Op1_MemberRegister() #등록절차 수행
        
    elif SelectedButtion == 2:
        pass 
    elif SelectedButtion == 3:
        pass
    elif SelectedButtion == 4:
        pass 
    elif SelectedButtion == 5:
        pass 
    elif SelectedButtion == 6:
        pass
    elif SelectedButtion == 7:
        
        Op7_ExitMenu()
              
    else :
        print('''\n****************************************************
누르신 항목이 메뉴에 없습니다. 다시 입력해주세요.
****************************************************\n''') 
        MenuList()
    
    


MenuList()









