from socket import *
from message import *
import threading
import sys
from user import *
from chatRoom import *

# user1 = User("kym8821")
# user1.save()
# user2 = User("louie9798")
# user2.save()
# user3 = User("postman")
# user3.save()
# user4 = User("cooing")
# user4.save()
# chatRoom1 = ChatRoom("kym8821", "louie9798")
# chatRoom2 = ChatRoom("postman", "louie9798")
# chatRoom3 = ChatRoom("cooing", "kym8821")
# chatRoom1.save()
# chatRoom2.save()
# chatRoom3.save()


userId = None
username = None

sendType = None
roomOrder = None

loginUserList = None
recvId = None
recvName = None

roomId = None
roomList = None

def printUserList():
    global loginUserList
    print("\n\nlogin user list : ")
    print(f"current login user amount : {len(loginUserList)}")
    for user in loginUserList: print(f"{user[0]} : {user[1]}")

def printRoomList():
    print("\n\nchat room list : ")
    print(f"current chat room amount : {len(roomList)}")
    for room in roomList: print("\t".join(room))

def receive_messages(client_socket):
    while True:
        global userId, username, recvId, recvName, loginUserList, sendType, roomList, roomOrder
        try:
            message = client_socket.recv(1024).decode('utf-8')
            top, message_type, body = resolve_message(message)
            #print(top, message_type, body)
            if message_type=="RECEIVE" and ( (recvId and sendType==1) or (roomId and roomOrder==2) ):
                sender = body[0].split(":")[1]
                receiver = body[1].split(":")[1]
                msg = body[2].split(":")[1]
                if sender!=username: print(f"{sender} : {msg}")
            elif message_type=="UPDATE_USER" and userId:
                body.pop()
                newLoginUserList = body
                _loginUserList = []
                for user in newLoginUserList:
                    user = user.split("\t")
                    if user[0] == userId : continue
                    _loginUserList.append(user)
                loginUserList = _loginUserList
                # 이미 receiver가 결정되었으면 continue
                if (sendType==2 and roomOrder==1) or (sendType==1 and not recvName):
                    # 양식 출력
                    printUserList()
                    print("user : ", end="")
            elif message_type=="UPDATE_ROOM" and userId:
                body.pop()
                newRoomList = body
                _roomList = []
                for room in newRoomList:
                    room = room.split("\t")
                    _roomList.append(room)
                roomList = _roomList
                if sendType==2 and not roomOrder:
                    # 양식 출력
                    printRoomList()
                    print("room id : ", end="")
        except Exception as e:
            print(e)
            client_socket.close()
            break

def send_messages(client_socket):
    global recvId, userId, username
    while True:
        message = input()
        if message == "quit":
            print("end program")
            break
        send_msg = generate_message("REQUEST", "SEND", f"sender:{userId}\r\nreceiver:{recvId}\r\nmessage:{message}")
        client_socket.send(send_msg.encode('utf-8'))

def login_user(client_socket):
    global userId, username, loginUserList  # 전역 변수 사용 선언
    userId = None
    username = None
    loginUserList = None
    while not userId:
        username = input("Username: ")  # 사용자로부터 username 입력 받음
        login_msg = generate_message("REQUEST", "LOGIN", f"username:{username}")
        client_socket.send(login_msg.encode("utf-8"))
        message = client_socket.recv(1024).decode("utf-8")
        top, message_type, body = resolve_message(message)
        #print(top, message_type, body)
        userId = body[0].split(":")[1]
        username = body[1].split(":")[1]

def getSendType():
    global sendType
    sendType = None
    while not sendType:
        print("\n\nSelect Send Type : ")
        print("[1] : send to user")
        print("[2] : group chat")
        print("[3] : logout")
        choice = input("your choice : ").strip()
        if choice=="1" : sendType = 1
        elif choice=="2" : sendType = 2
        elif choice=="3" : sendType = 3
        else : print("invalid send Type")

def getRoomId():
    global roomId, roomList
    roomId = None
    while not roomId:
        _roomId = input()
        for user in loginUserList:
            if _roomId == user[0]: 
                roomId = _roomId
        if not recvId : print("invalid room id")

def getReceiverId():
    global loginUserList, recvId, recvName
    recvId = None
    recvName = None
    while not recvId:
        _rid = input()
        for user in loginUserList:
            if _rid == user[0]: 
                recvId = user[0]
                recvName = user[1]
        if not recvId : print("invalid user id")

def getRoomId():
    global roomList, roomId
    roomId = None
    while not roomId:
        _roomId = input()
        for room in roomList:
            if _roomId == room[0]:
                roomId = room[0]
        if not roomId : print("invalid room id")

def send_message_to_room(client_socket):
    global userId, roomId, username
    while True:
        message = input()
        if message == "quit": break
        #print(f"{username}:{message}")
        #send_msg = f"SEND_ROOM\r\nroomId:{roomId}\r\nuserId:{userId}\r\nmessage:{message}"
        send_msg = generate_message("REQUEST", "SEND_ROOM", f"roomId:{roomId}\r\nuserId:{userId}\r\nmessage:{message}")
        client_socket.send(send_msg.encode('utf-8'))

def getRoomOrder():
    global roomList, roomId, roomOrder
    roomOrder = None
    while not roomOrder:
        print("\n\nSelect Send Type : ")
        print("[1] : join user")
        print("[2] : enter group chat")
        print("[3] : quit")
        _roomOrder = input("your choice : ").strip()
        if _roomOrder=="1" : roomOrder = 1
        elif _roomOrder=="2" : roomOrder = 2
        elif _roomOrder=="3" : roomOrder = 3
        else : print("invalid send Type")

def joinUser(client_socket):
    global roomId
    join_user = None
    while not join_user:
        name = input()
        for user in loginUserList:
            if name == user[1]: 
                join_user = name
        if not join_user : 
            print("invalid user name")
            print("user : ")
    # join_msg = f"JOIN\r\nroomId:{roomId}\r\nusername:{join_user}"
    join_msg = generate_message("REQUEST", "JOIN", f"roomId:{roomId}\r\nusername:{join_user}")
    client_socket.send(join_msg.encode("utf-8"))

def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 8000))
    while True:
        # login_user 함수를 스레드로 실행
        login_user_thread = threading.Thread(target=login_user, args=(client_socket,))
        login_user_thread.start()
        login_user_thread.join()  # 로그인 완료될 때까지 기다림

        while True:
            # send type 결정
            sendType_thread = threading.Thread(target=getSendType)
            sendType_thread.start()
            sendType_thread.join()

            listen_thread = threading.Thread(target=receive_messages, args=(client_socket,))
            # connect_msg = f"CONNECT\r\nuserId:{userId}\r\nusername:{username}"
            connect_msg = generate_message("REQUEST", "CONNECT", f"userId:{userId}\r\nusername:{username}")
            client_socket.send(connect_msg.encode("utf-8"))
            listen_thread.start()
            # 일대일 채팅 기능
            if sendType == 1:
                # receiver 결정
                receiver_thread = threading.Thread(target=getReceiverId)
                receiver_thread.start()
                receiver_thread.join()
                # 송신 스레드 시작
                print(f"enter chat room : {username} & {recvName}")
                print("if you want to go out, type 'quit'!!")
                sendThread = threading.Thread(target=send_messages, args=(client_socket,))
                sendThread.start()
                sendThread.join()
            # 다대다 채팅 기능
            elif sendType == 2:
                # chat room 결정
                room_thread = threading.Thread(target=getRoomId) 
                room_thread.start()
                room_thread.join()
                # user join과 enter chatroom 중 하나 선택
                room_order_thread = threading.Thread(target=getRoomOrder)
                room_order_thread.start()
                room_order_thread.join()
                # user join
                if roomOrder == 1:
                    printUserList()
                    print("user : ", end="")
                    join_thread = threading.Thread(target=joinUser, args=(client_socket, ))
                    join_thread.start()
                    join_thread.join()
                # join room
                elif roomOrder == 2:
                    print(f"enter chat room : {username} & {recvName}")
                    print("if you want to go out, type 'quit'!!")
                    send_message_to_room_thread = threading.Thread(target=send_message_to_room, args=(client_socket, ))
                    send_message_to_room_thread.start()
                    send_message_to_room_thread.join()
            # 로그인 화면으로 돌아가기
            elif sendType == 3:
                break
        # disconnect_msg = f"DISCONNECT\r\nuserId:{userId}"
        disconnect_msg = generate_message("REQUEST", "DISCONNECT", f"userId:{userId}")
        client_socket.send(disconnect_msg.encode("utf-8"))
        
if __name__ == "__main__":
    start_client()
    print("end")
    sys.exit(0)