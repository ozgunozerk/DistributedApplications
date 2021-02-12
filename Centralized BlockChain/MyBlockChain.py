# UNCOMMENT THIS AFTER TEST
import Pyro4


class Block:
    def __init__(self, transaction):
        self.transaction = transaction
        self.next = None

# UNCOMMENT THIS AFTER TEST
@Pyro4.expose
class MyBlockChain:
    def __init__(self, name):
        self.head = None
        self.name = name
        # register object itself
        # UNCOMMENT THIS AFTER TEST
        #'''
        daemon = Pyro4.Daemon()
        Pyro4.locateNS().register(self.name, daemon.register(self))
        print(self.name, "server is ready...")
        daemon.requestLoop()
        #'''


    def getName(self):
        return self.name


    def insertTx(self, transaction):
        new_Block = Block(transaction)  # create a new Block

        if self.head != None:  # if linked list has blocks in it
            new_Block.next = self.head

        self.head = new_Block  # set its new head


    def findAccount(self, ID):
        traverse_node = self.head

        while traverse_node != None:  # iterate until (CREATEACCOUNT, (ID, amount)) is encountered, or list is done
            if traverse_node.transaction[0] == "CREATEACCOUNT":  # if this is a createAccount block
                if traverse_node.transaction[1][0] == ID:  # means we have found the user
                    return True
            traverse_node = traverse_node.next

        return False


    def calculateBalance(self, ID):  
        traverse_node = self.head
        balance = 0

        while traverse_node != None:
            transaction = traverse_node.transaction
            if transaction[0] == "CREATEACCOUNT":
                if transaction[1][0] == ID:
                    balance += transaction[1][1]
            
            else:  # means it's an exchange or transfer block
                if transaction[1][0] == ID:  # if ID matches with 'from_account'
                    balance -= transaction[1][-1]  # transaction args last element is the amount
                
                elif transaction[1][1] == ID:  # if ID matches with 'to_account'
                    balance += transaction[1][-1]  # transaction args last element is the amount
            
            traverse_node = traverse_node.next  # iterate through the list
        
        return balance

        
    def createAccount(self, amount):
        traverse_node = self.head
        new_ID = 0  

        while traverse_node != None:  # traverse the list
            if traverse_node.transaction[0] == "CREATEACCOUNT":  # means we have found an account
                new_ID = traverse_node.transaction[1][0]  # transaction = (CREATEACCOUNT, (ID, amount))
                new_ID += 1  # assign a unique ID to new user
                break  # the last item is already the maximum right? No need to traverse all the list :) 
            traverse_node = traverse_node.next
        
        else:  # means list is empty
            new_ID = 1

        new_transaction = ("CREATEACCOUNT", (new_ID, amount))  # create the new transaction
        self.insertTx(new_transaction)  # insert this transaction into BLOCKCHAIN

        return new_ID


    def transfer(self, from_account, to_account, amount):  
        reverse = False
        if amount < 0:  # if amount is negative, it's a reverse transaction
            reverse = True

        if self.findAccount(from_account) and self.findAccount(to_account):  # if both accounts exist

            if reverse:  # amount is negative ==> money is transferred like: to_account -> from_account

                if -amount <= self.calculateBalance(to_account):  # if sender has enough money.  -amount, since it's a reverse operation
                    new_transaction = ("TRANSFER", (from_account, to_account, amount)) 

                else:  # the sender account does not have enough money
                    return -1 
            
            else:  # amount is positive ==> money is transferred like: from_account -> to_account

                if amount <= self.calculateBalance(from_account):  # if sender has enough money
                    new_transaction = ("TRANSFER", (from_account, to_account, amount)) 

                else:  # the sender account does not have enough money
                    return -1 
        
        else:  # at least 1 of the (from_account, to_account) couple is missing in the chain
            return -1

        self.insertTx(new_transaction)
        return 1



    # UNCOMMENT THIS AFTER TEST
    #'''  
    def exchange(self, from_account, to_account, toChain, amount):
        reverse = False
        if amount < 0:  # if amount is negative, it's a reverse transaction
            reverse = True

        #remote_chain = Pyro4.Proxy("PYRONAME:" + toChain)
        if self.findAccount(from_account) and toChain.findAccount(to_account):  # if both accounts exist

            if reverse:  # amount is negative ==> money is transferred like: to_account -> from_account

                if -amount <= toChain.calculateBalance(to_account):  # if sender has enough money.  -amount, since it's a reverse operation
                    this_transaction = ("EXCHANGE", (from_account, to_account, toChain.getName(), amount))
                    remote_transaction = ("EXCHANGE", (to_account, from_account, self.name, -amount))

                else:  # sender does not have enough money
                    return -1

            else:  # amount is positive ==> money is transferred like: from_account -> to_account

                if amount <= self.calculateBalance(from_account):
                    this_transaction = ("EXCHANGE", (from_account, to_account, toChain.getName(), amount))
                    remote_transaction = ("EXCHANGE", (to_account, from_account, self.name, -amount))
                    
                else: # sender does not have enough money
                    return -1

        else:  # at least 1 of the (from_account, to_account) couple is missing in their respective chain
            return -1

        self.insertTx(this_transaction)
        toChain.insertTx(remote_transaction)
        return 1

    #'''


    # below is the same function, but it gets the other chain as a string parameter instead of a pyro object
    '''  
    def exchange(self, from_account, to_account, toChain, amount):
        reverse = False
        if amount < 0:  # if amount is negative, it's a reverse transaction
            reverse = True

        remote_chain = Pyro4.Proxy("PYRONAME:" + toChain)
        if self.findAccount(from_account) and remote_chain.findAccount(to_account):  # if both accounts exist

            if reverse:  # amount is negative ==> money is transferred like: to_account -> from_account

                if -amount <= remote_chain.calculateBalance(to_account):  # if sender has enough money.  -amount, since it's a reverse operation
                    this_transaction = ("EXCHANGE", (from_account, to_account, toChain, amount))
                    remote_transaction = ("EXCHANGE", (to_account, from_account, self.name, -amount))

                else:  # sender does not have enough money
                    return -1

            else:  # amount is positive ==> money is transferred like: from_account -> to_account

                if amount <= self.calculateBalance(from_account):
                    this_transaction = ("EXCHANGE", (from_account, to_account, toChain, amount))
                    remote_transaction = ("EXCHANGE", (to_account, from_account, self.name, -amount))
                    
                else: # sender does not have enough money
                    return -1

        else:  # at least 1 of the (from_account, to_account) couple is missing in their respective chain
            return -1

        self.insertTx(this_transaction)
        remote_chain.insertTx(remote_transaction)
        return 1
    '''

    def printChain(self):
        traverse_node = self.head

        while traverse_node != None:  # traverse the list
            print(traverse_node.transaction)
            traverse_node = traverse_node.next