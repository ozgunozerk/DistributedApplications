from FindCitations import FindCitations
from FindCyclicReferences import FindCyclic
import sys

if len(sys.argv) != 4:
    print("Please enter the METHOD, WORKER_AMOUNT, and FILENAME as parameter")

method = sys.argv[1]
worker_amount = int(sys.argv[2])
filename = sys.argv[3]

if worker_amount > 10 or worker_amount < 1:
    print("please enter the worker amount something between [1-10]")


if __name__ == '__main__':
    if method.lower() == "cyclic":
        mr = FindCyclic(worker_amount)
        print("Find Cyclic has been called")
        mr.start(filename)


    elif method.lower() == "count":
        mr = FindCitations(worker_amount)
        print("Find Citations has been called")
        mr.start(filename)



