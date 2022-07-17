
class Queue():
    def __init__(self, top, jungle, mid, bottom, support, acceptCheck):
        self.top = top
        self.jungle = jungle
        self.mid = mid
        self.bottom = bottom
        self.support = support
        self.acceptCheck = acceptCheck

    def checkQueue(self):
        if len(self.top) >= 2 and len(self.jungle) >= 2 and len(self.mid) >= 2 and len(self.bottom) >= 2 and len(self.support) >= 2 : # and len(self.jungle) >= 2 and len(self.mid) >= 2 and len(self.bottom) >= 2 and len(self.support) >= 2
            return 1
        else:
            return 0

    def enterQueue(self, id):
        try:
            for m in range(len(self.top)): # Deletes user from the list of dictionaries using ID
                i = self.top[m]
                value = list(i.values())
                if value[0] == id:
                    del(self.top[m])

            for m in range(len(self.jungle)):
                i = self.jungle[m]
                value = list(i.values())
                if value[0] == id:
                    del(self.jungle[m])

            for m in range(len(self.mid)):
                i = self.mid[m]
                value = list(i.values())
                if value[0] == id:
                    del(self.mid[m])

            for m in range(len(self.bottom)):
                i = self.bottom[m]
                value = list(i.values())
                if value[0] == id:
                    del(self.bottom[m])

            for m in range(len(self.support)):
                i = self.support[m]
                value = list(i.values())
                if value[0] == id:
                    del(self.support[m])
        except:
            pass


if __name__ == '__main__':
    Queue()