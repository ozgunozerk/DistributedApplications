import MyBlockChain

test =  MyBlockChain.LinkedList('wow')

user1 = test.createAccount(100)
user2 = test.createAccount(50)
user3 = test.createAccount(20)
user4 = 4

operation1 = test.transfer(user1, user2, 10)
operation2 = test.transfer(user3, user2, 30)
operation3 = test.transfer(user1, user3, 20)
operation4 = test.transfer(user2, user3, -30)
operation5 = test.transfer(user4, user1, 10)

print(operation1, operation2, operation3, operation4, operation5)
