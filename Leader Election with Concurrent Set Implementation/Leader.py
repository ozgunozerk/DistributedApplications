import threading
import time
import random

from ConSet import MyConSet

equality = True  # global variable for storing the condition of equality


n = 3  # player amount

# creation of mailboxes
globalList = []
for x in range(n):
    globalList.append(MyConSet())



def nodeWork(id, n):  # a player
    global equality
    rnd = random.randint(1, n-1)  # generate a random number    FIX THISS!! N*N
    aTuple = (id, rnd)  # make it a tuple (id, random_num)
    for x in range(n):  # for every mailbox (incuding its own)
        print("Thread id:", id, "inserted:", aTuple)
        globalList[x].insert(aTuple)  # send the tuple to mailboxes

    Leader = 0  # for storing the Leader's identity
    maximum = 0  # for storing the maximum number
    secondMaximum = 0  # for storing the second maximum, to see if there is equality

    # algorithm to find the biggest 2 values in the list
    for x in range(n):
        try:
            current = globalList[id].pop()
            print("Thread id:", id, "popped:", current)
        except:
            current = globalList[id].pop()
            print("EXCEPTION HANDLED: Thread id:", id, "popped:", current)
        
        if current[1] >= maximum:
            secondMaximum = maximum
            maximum = current[1]
            Leader = current[0]
    
    if secondMaximum != maximum:  # if there is equality
        equality = False  # update the boolean, no race condition here, so no need for locks
        print("My Leader is:", Leader)




##############
# MAIN
##############
threadList = []

round = 0

while(equality):
    print("-------------")
    print("Round:", round)
    print("-------------\n")
    for id in range(n):
        t = threading.Thread(target=nodeWork, args=([id, n]))
        t.start()
        threadList.append(t)
    
    for id in range(n):
        threadList[id].join()
    
    print("Equality:", equality)
    threadList.clear()
    round += 1
    time.sleep(1)
a = 5
b = 3









