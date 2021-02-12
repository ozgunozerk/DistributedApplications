import random
from multiprocessing import Process
from threading import Thread
import os
import zmq
import time
import sys

# DONT FORGET TO TAKE PARAMETERS FROM SYS ARGUMENTS


# ------
# LEADER
# ------ 
def leader(ID, is_starter, total_node_amount):  # process target
    global should_participate
    global will_terminate

    pid = os.getpid()
    print("PROCESS STARTS", pid, ID, is_starter)

    listener = Thread(target=responder, args=(ID, total_node_amount,))
    listener.start()


    participated = False  # flag to limit broadcasting to only 1 time (can be written to by main thread)
    should_participate = False  # flag to limit broadcasting to only 1 time (can be written to by listener thread)
    will_terminate = False  # flag to control if a terminate message has arrived
    response_count = 0  # int variable to store current response amount

    port = 5550 + ID
    ctx = zmq.Context()
    mysocket = ctx.socket(zmq.PUB)
    mysocket.bind(f"tcp://127.0.0.1:{port}")

    time.sleep(0.5)
    
    poller = zmq.Poller()  # poller for iterating through all responder sockets
    responder_list = []  # list to store all responder sockets
    for responder_id in range(total_node_amount):  # for each alive respodner, connect to it's socket
        socket = ctx.socket(zmq.SUB)
        port = 5550 - (responder_id + 1)
        socket.connect(f"tcp://127.0.0.1:{port}")
        socket.subscribe("RESPONSE")  # subscribce to RESPONSE
        poller.register(socket, zmq.POLLIN)  # register this socket to the poller
        responder_list.append(socket)  # add this socket to the socket list

    time.sleep(1)

    if is_starter:
        # Sends multipart message to subscriber
        mysocket.send_string("LEADER", flags=zmq.SNDMORE)
        mysocket.send_string(f"PROCESS MULTICASTS LEADER MSG: {ID}")
        print(f"PROCESS MULTICASTS LEADER MSG: {ID}")
        # mutex lock here
        participated = True
        # mutex unlock here

    

    while not(will_terminate):  # has not received any terminate signal, 
        #print(f"LEA PRO {ID} in while loop, participated: {participated}")
        if (not(participated) and should_participate):
            mysocket.send_string("LEADER", flags=zmq.SNDMORE)
            mysocket.send_string(f"PROCESS MULTICASTS LEADER MSG: {ID}")
            print(f"PROCESS MULTICASTS LEADER MSG: {ID}")
            # mutex lock here
            participated = True
            should_participate = False

        #print(f"LEA PRO {ID} in while loop, participated: {participated}, response count: {response_count}")
        if (participated and response_count == 0):
            
            timeout1 = time.time() + (1)  # timeout set for 4 seconds later from now
            while time.time() < timeout1:  # while loop with 4 second timeout
                evts = dict(poller.poll(timeout=100))
                for socket in responder_list:   
                    if socket in evts:
                        topic = socket.recv_string()
                        if topic == "RESPONSE":                            
                            status = socket.recv_string()
                            responding_to_id = int(status[status.rfind(" ") + 1 :])
                            #print("my id ", ID, " i get response from ", status)
                            if ID == responding_to_id:
                                response_count += 1
                time.sleep(0.01)
            
            #print("my id ", ID, " my responsse count ", response_count)
            if response_count == 0:
                mysocket.send_string("TERMINATE", flags=zmq.SNDMORE)                
                mysocket.send_string(f"PROCESS MULTICASTS LEADER MSG: {ID}")
                print(f"PROCESS BROADCASTS TERMINATE MSG: {ID}")
                will_terminate = True
    
    listener.join()


# ------
# RESPONDER
# ------ 
def responder(ID, total_node_amount):  # thread target
    global should_participate
    global will_terminate

    print(f"RESPONDER STARTS: {ID}")

    ctx = zmq.Context()

    # create it's own socket for response mechanism
    mysocket = ctx.socket(zmq.PUB)
    port = 5550 - (ID + 1)   # ID + 1 , because ID = 0 will be on the same port
    mysocket.bind(f"tcp://127.0.0.1:{port}")

    time.sleep(0.5)

    poller = zmq.Poller()  # poller for iterating through all leader sockets
    leader_list = []  # list to store all leader sockets
    for leader_id in range(total_node_amount):  # for each alive leader, connect to it's socket
        socket = ctx.socket(zmq.SUB)
        port = 5550 + leader_id
        socket.connect(f"tcp://127.0.0.1:{port}")
        socket.subscribe("LEADER")  # subscribce to LEADER
        socket.subscribe("TERMINATE")  # subscribce to TERMINATE
        poller.register(socket, zmq.POLLIN)  # register this socket to the poller
        leader_list.append(socket)  # add this socket to the socket list
    
    time.sleep(1)

    

    will_terminate = False
    while not(will_terminate):
        
    #timeout = time.time() + (alive_node_amount * 2)
    #while time.time() < timeout:    
        evts = dict(poller.poll(timeout=100))
        for socket in leader_list:
            if socket in evts:
                topic = socket.recv_string()
                status = socket.recv_string()
                #print(f"Message: {topic} => {status}")
                if topic == "LEADER":
                    #message = status["message"]
                    #print(f"Responder {ID} received message {status}")
                    leaderID = int(status[status.rfind(" ") + 1 :])
                    if int(leaderID) < ID:
                        #print(f"I'm {ID} bigger than {leaderID}")
                        mysocket.send_string("RESPONSE", flags=zmq.SNDMORE)
                        mysocket.send_string(f"RESPONDER RESPONDS: {ID} {leaderID}")
                        print(f"RESPONDER RESPONDS: {ID} {leaderID}")
                        should_participate = True

                if topic == "TERMINATE":
                    #print(f"PROCESS {ID}, received terminate message")
                    will_terminate = True
                    break
        time.sleep(0.1)
    

                
        

# ------
# MAIN
# ------ 

# list generation for all processes

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Next time, please enter the #Processes, #Alives, and #Starters as parameter")
        exit()

    total_node_amount = int(sys.argv[1])
    alive_node_amount = int(sys.argv[2])
    starter_node_amount = int(sys.argv[3])

    if not (starter_node_amount < alive_node_amount < total_node_amount):
        print("It should have been:")
        print("#Starters < #Alives < #Processors")
        exit()

    process_id_list = []
    alive_id_list = []
    starter_id_list = []



    process_id_list = list(range(0, total_node_amount))
    #print("process id list")
    #print(process_id_list)
    alive_id_list = random.sample(process_id_list, alive_node_amount)
    #print("alive_id_list")
    #print(alive_id_list)
    starter_id_list = random.sample(alive_id_list, starter_node_amount)
    #print("starter_id_list")
    #print(starter_id_list)


    #print("All processes:", process_id_list)
    print("Alives:")
    print(alive_id_list)
    print("Starters:")
    print(starter_id_list)


    # creating processes for each alive node
    alive_process_list = []
    for x in range(len(alive_id_list)):
        is_starter = (alive_id_list[x] in starter_id_list)
        an_alive_process = Process(target=leader, args=(alive_id_list[x], is_starter, total_node_amount,))
        alive_process_list.append(an_alive_process)


    for x in alive_process_list:
        x.start()

    for x in alive_process_list:
        x.join()