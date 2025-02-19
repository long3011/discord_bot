import random

class User:
    def __init__(self, id, balance=1000):
        self.id = id
        self.balance = balance

    def coin_flip(self, amount):
        result=random.choice([True, False])
        if result:
            self.balance += amount
            return True
        else:
            self.balance -= amount
            return False
    def add_coin(self, amount):
        self.balance += amount