from abc import ABC, abstractmethod
import zmq, os, time
from multiprocessing import Process, Value, Array


class MapReduce(ABC):

    worker_amount = 0
    worker_list = []

    def __init__(self, workerAmount):  # constructor
        self.worker_amount = workerAmount

    @abstractmethod  # abstract
    def Map(self, map_input):
        pass

    @abstractmethod  # abstract
    def Reduce(self, reduce_input):  
        pass

    def _Producer(self, producer_input):  # private

        work_size = len(producer_input)  # how many total works we have
        base_work_amount = work_size // self.worker_amount
        leftover_work_amount = work_size - base_work_amount * self.worker_amount

        work_amount_list = []
        # assigning base_work_amount to every worker
        for worker in range(self.worker_amount):
            work_amount_list.append(base_work_amount)

        # assigning leftover works to first workers
        for work in range(leftover_work_amount):
            work_amount_list[work] += 1

        
        # create the socket 
        '''
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://127.0.0.1:5558")

        # push works into the socket
        counter = 0
        work_list = []
        for work_amount in work_amount_list:
            work_list.append(producer_input[counter : counter + work_amount])
            counter += work_amount

        for work in work_list:
            socket.send_json(work)
            time.sleep(0.01)  # if any error happens, increase this
        '''
        counter = 0
        for ID in range(self.worker_amount):
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)
            socket.connect("tcp://127.0.0.1:" + str(5559 + ID))
            work = producer_input[counter : counter + work_amount_list[ID]]
            counter += work_amount_list[ID]
            socket.send_json(work)


        return

    def _Consumer(self, ID):  # private
        pid = os.getpid()
        print("Consumer PID:", pid)
        
        # getting work
        '''
        context = zmq.Context()
        get_work = context.socket(zmq.PULL)
        get_work.connect("tcp://127.0.0.1:5558")
        '''

        # getting work
        context = zmq.Context()
        get_work = context.socket(zmq.PULL)
        get_work.bind("tcp://127.0.0.1:" + str(5559 + ID))
        work = get_work.recv_json()
        
        print("Map", pid, "Input:", work)

        # submitting work to map
        partial_result = self.Map(work)  # must be dictionary

        print("Map", pid, "Result:", partial_result)

        
        # submitting result to reduce
        '''
        context = zmq.Context()
        submit_work = context.socket(zmq.PUSH)
        submit_work.bind("tcp://127.0.0.1:" + str(5559 + local_id))
        submit_work.send_json(partial_result)
        '''
        # submitting result to reduce
        context = zmq.Context()
        submit_work = context.socket(zmq.PUSH)
        submit_work.connect("tcp://127.0.0.1:5558")
        submit_work.send_json(partial_result)

        return

    def _ResultCollector(self):  # private
        print("Result Collector PID:", os.getpid())
        partial_works = []

        # getting partial results
        '''
        for ID in range(self.worker_amount):
            context = zmq.Context()
            get_partial_work = context.socket(zmq.PULL)
            get_partial_work.connect("tcp://127.0.0.1:" + str(5559 + ID))

            partial_work = get_partial_work.recv_json()
            partial_works.append(partial_work)
        '''

        # getting partial results
        context = zmq.Context()
        submit_work = context.socket(zmq.PULL)
        submit_work.bind("tcp://127.0.0.1:5558")
        for ID in range(self.worker_amount):
            partial_work = submit_work.recv_json()
            partial_works.append(partial_work)

        print("Reducer data:", partial_works)
        
        # get the final work
        final_result = self.Reduce(partial_works)

        print("Results:", final_result)



        # write the final result into results.txt
        f = open("results.txt", 'w')
        f.write(str(final_result))
        f.close()
        
        
        return 

    def start(self, fileName):  # public

        # reading the file, and creating the list of lines
        file_content = []
        the_file = open(fileName, "r")
        for line in the_file:  # splitting every line with respect to TAB
            if line != "\n":
                list_int = [int(x) for x in line.strip().split("\t")]
                file_content.append(list_int)
            
        the_file.close()
        print("Initial Data:", file_content)

        for ID in range(self.worker_amount):  # creating the worker processes
            a_consumer = Process(target=self._Consumer, args=(ID,))
            self.worker_list.append(a_consumer)
        
        # creating the producer process, and supplying the file_content to it
        the_producer = Process(target=self._Producer, args=(file_content,))

        # creating the collector process
        the_collector = Process(target=self._ResultCollector, args=())

        
        the_collector.start()
        for worker in self.worker_list:
            worker.start()
        the_producer.start()
        


        the_producer.join()
        for worker in self.worker_list:
            #worker.terminate()
            worker.join()
        the_collector.join()
        #the_collector.terminate()
        
        

        return
