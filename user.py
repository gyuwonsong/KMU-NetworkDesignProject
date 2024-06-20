class User:
    div = "\t"

    def getNextId(self):
        with open("./db/user.txt", 'r') as f:
            try:
                data = f.readlines()
                cdn = len(data)
                if cdn == 0: return 1
                lastUserId = int((data[-1].split("\t"))[0].strip("\n"))
                return lastUserId+1
            except Exception as e:
                print(e)
            finally:
                f.close()

    def __init__(self, name, id=None):
        nextId = self.getNextId()

        self.id = nextId
        self.name = name

    def __str__(self):
        return str(self.id) + self.div + str(self.name) + self.div + "\n"

    def save(self):
        strUser = str(self)
        with open("./db/user.txt", "a") as db:
            try:
                db.write(strUser)
            finally:
                db.close()
    
    @staticmethod
    def getUserIdByName(name):
        with open("./db/user.txt", "r") as db:
            try:
                dataList = db.readlines()
                for data in dataList:
                    userData = data.strip("\n").split("\t")
                    if userData[1] == name:
                        return userData[0]
                return False
            except Exception as e:
                print(e)
    @staticmethod
    def getUsernameById(id):
        with open("./db/user.txt", "r") as db:
            try:
                dataList = db.readlines()
                for data in dataList:
                    userData = data.strip("\n").split("\t")
                    if userData[0] == id:
                        return userData[1]
                return False
            except Exception as e:
                print(e)
def toUser(user):
    arr = user.split(User.div)
    try:
        id = int(arr[0])
        name = arr[1]
        return User(name, id=id)
    except:
        print("invalid user")
        return None