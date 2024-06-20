class ChatRoom:
    @staticmethod
    def join(roomId, *users):
        with open("./db/chatroom.txt", "r+") as db:
            try:
                dataList = db.readlines()
                currentChatRoom = None
                currentChatRoomIdx = None
                if not dataList: return "db is empty"
                for idx, data in enumerate(dataList):
                    chatRoomData = data.strip("\n").split("\t")
                    print(chatRoomData[0], roomId)
                    if int(chatRoomData[0]) == roomId:
                        currentChatRoom = chatRoomData
                        currentChatRoomIdx = idx
                        break
                if not currentChatRoom:
                    return "invalid roomId"
                for user in users:
                    for existUser in currentChatRoom:
                        if user == existUser: return "users already exists"
                dataList[currentChatRoomIdx] = (dataList[currentChatRoomIdx]).strip("\n")
                for user in users: dataList[currentChatRoomIdx]+=("\t" + user)
                dataList[currentChatRoomIdx]+="\n"
                db.seek(0)  
                db.truncate()
                db.writelines(dataList)
                return "success"
            except Exception as e:
                print(e)
            finally:
                db.close()

    @staticmethod
    def getNextId():
        with open("./db/chatroom.txt", 'r') as f:
            try:
                f.seek(0)
                data = f.readlines()
                print(data)
                cdn = len(data)
                print(cdn)
                if cdn == 0: return 1
                lastUserId = int((data[-1].split("\t"))[0].strip("\n"))
                return lastUserId+1
            except Exception as e:
                print(e)
            finally:
                f.close()
    
    @staticmethod
    def getChatRoomByUser(user):
        chatRoomList = []
        with open("./db/chatroom.txt", 'r') as db:
            dataList = db.readlines()
            for data in dataList:
                chatRoom = data.strip("\n").split("\t")
                for idx in range(1, len(chatRoom)):
                    existUser = chatRoom[idx]
                    if(user == existUser):
                        chatRoomList.append(chatRoom)
                        db.close()
                        break
        return chatRoomList

    @staticmethod
    def getUserListByRoomId(roomId):
        userList = []
        with open("./db/chatroom.txt", 'r') as db:
            dataList = db.readlines()
            for data in dataList:
                chatRoom = data.strip("\n").split("\t")
                if chatRoom[0] == str(roomId):
                    userList = chatRoom[1:]
                    db.close()
                    break
        return userList

    def __init__(self, *users):
        self.userList = []
        for user in users:
            self.userList.append(user)
        self.id = -1

    def save(self):
        self.id = self.getNextId()
        with open("./db/chatroom.txt", 'a') as db:
            try:
                strChatRoom = str(self)
                db.write(strChatRoom)
            except Exception as e:
                print(e.with_traceback())

    def __str__(self):
        strChatRoom = str(self.id)
        for user in self.userList:
            strChatRoom += "\t" + user
        return strChatRoom + "\n"