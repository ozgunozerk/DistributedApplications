import threading
import time

class MyConSet:

    def __init__(self):
        self.set = {}
        self.lock = threading.Lock()


    def insert(self, newItem):

        self.lock.acquire(blocking=True)

        # critical region start
        self.set[newItem] = True
        
        # critical region end

        self.lock.release()


    def pop(self):

        while True:
            for key in self.set.keys():

                self.lock.acquire(blocking=True)

                # critical region start
                curr = self.set[key]
                self.set[key] = False
                # critical region end

                self.lock.release()
                time.sleep(0.3)

                if curr != False:
                    return key

            print ("Dequeue could not find an element")


    def printSet(self):
        for key,value in self.set.items():
            print(key, value)

'''
mySet = MyConSet()
mySet.printSet()


t1 = threading.Thread(target=mySet.pop)
t1.start()

t2 = threading.Thread(target=mySet.insert, args=([(3, True)]))
t2.start()



t1.join()
t2.join()
t3.join()

mySet.printSet()
'''