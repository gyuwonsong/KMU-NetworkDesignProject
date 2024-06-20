import socket
import threading
from userManager import UserManager
from user import *
from chatRoom import *
from message import *

# 서버 정보 설정
HOST = '127.0.0.1'  # 로컬 호스트
PORT = 8000  # 사용할 포트 번호

# 로그인한 클라이언트 목록 저장
userManager = UserManager()

# 클라이언트로부터 메시지를 받는 함수
def handle_client(client_socket):
    current_user_id = None

    while True:
        try:
            message = (client_socket.recv(1024).decode('utf-8'))
            top, message_type, body = resolve_message(message)
            print(top, message_type, body)
            if message_type == "SEND":
                senderId = body[0].split(":")[1]
                receiverId = body[1].split(":")[1]
                msg = body[2].split(":")[1]
                sendToUser(senderId, receiverId, msg)
            elif message_type == "SEND_ROOM":
                roomId = body[0].split(":")[1]
                userId = body[1].split(":")[1]
                msg = body[2].split(":")[1]
                userList = ChatRoom.getUserListByRoomId(roomId=roomId)
                for user in userList:
                    senderId = userId
                    receiverId = User.getUserIdByName(user)
                    sendToUser(senderId, receiverId, msg)
            elif message_type == "JOIN":
                roomId = body[0].split(":")[1]
                username = body[1].split(":")[1]
                print(roomId, username)
                print(ChatRoom.join(int(roomId), username))
                # 채팅방 목록 갱신
                sendRoomListToUser()
            elif message_type == "LOGIN":
                username = body[0].split(":")[1]
                userId = User.getUserIdByName(username)
                # loginMsg = (f"LOGIN\r\nuserId:{userId}\r\nusername:{username}")
                login_msg = generate_message("RESPONSE", "LOGIN", f"userId:{userId}\r\nusername:{username}")
                print(login_msg)
                current_user_id = userId
                client_socket.send(login_msg.encode("utf-8"))
            elif message_type == "CONNECT":
                userId = body[0].split(":")[1]
                username = body[1].split(":")[1]
                userManager.add(userId, username, client_socket)
                # 사용자 목록 갱신
                # update_msg = "UPDATE_USER\r\n" + userManager.toResDto()
                update_msg = generate_message("RESPONSE", "UPDATE_USER", userManager.toResDto())
                print(update_msg)
                sendAll(update_msg)
                # 채팅방 목록 갱신
                sendRoomListToUser()
            elif message_type == "DISCONNECT":
                userId = body[0].split(":")[1]
                userManager.delete(userId=userId)
                current_user_id = None
        except Exception as e:
            if current_user_id: userManager.delete(current_user_id)
            print(e)
            break
    # 사용자 목록 재갱신
    # update_msg = "UPDATE_USER\r\n" + userManager.toResDto()
    update_msg = generate_message("RESPONSE", "UPDATE_USER", userManager.toResDto())
    sendAll(update_msg)
    
def sendRoomListToUser():
    for user in userManager.userList:
        username = user["username"]
        chatRoomList = ChatRoom.getChatRoomByUser(username)
        chatRoomStr = ""
        for chatRoom in chatRoomList:
            chatRoomStr+="\t".join(chatRoom) + "\r\n"
        #update_room_msg = "UPDATE_ROOM\r\n" + chatRoomStr
        update_room_msg = generate_message("RESPONSE", "UPDATE_ROOM", chatRoomStr)
        user["socket"].send(update_room_msg.encode("utf-8"))

def sendAll(message):
    for user in userManager.userList:
        user["socket"].send(message.encode("utf-8"))

# 메시지를 모든 클라이언트에게 브로드캐스트하는 함수
def sendToUser(senderId, receiverId, msg):
    sender = User.getUsernameById(senderId)
    receiver = User.getUsernameById(receiverId)
    # receive_msg = f"RECEIVE\r\nsender:{sender}\r\nreceiver:{receiver}\r\nmessage:{msg}"
    receive_msg = generate_message("RESPONSE", "RECEIVE", f"sender:{sender}\r\nreceiver:{receiver}\r\nmessage:{msg}")
    print(receive_msg)
    for client in userManager.userList:
        print(client["userId"], receiverId)
        if client["username"] == receiver:
            print(f"broadcast msg to {receiverId}")
            print(client["socket"])
            client["socket"].send(receive_msg.encode('utf-8'))

# 서버 설정 및 클라이언트 연결 수락
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"서버가 {HOST}:{PORT}에서 시작되었습니다.")

    while True:
        client_socket, client_address = server.accept()
        print(f"{client_address}가 연결되었습니다.")

        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()