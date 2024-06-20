class UserManager():
    def __init__(self):
        self.userList = []

    def add(self, userId, username, client_socket):
        for user in self.userList:
            if user["username"] == username: self.userList.remove(user)
        self.userList.append({"userId":userId, "username":username, "socket":client_socket})
    
    def delete(self, userId):
        for user in self.userList:
            if user["userId"] == userId:
                self.userList.remove(user)
                return True
        return False
    
    def toResDto(self):
        res = ""
        for user in self.userList:
            strUser = f'{user["userId"]}\t{user["username"]}\r\n'
            res+=strUser
        return res