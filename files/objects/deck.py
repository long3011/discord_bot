import random


class Deck:
    def __init__(self, size):
        self.cards = []
        for x in range(size):
            for i in range(13):
                for j in ["clubs", "diamonds", "hearts", "spades"]:
                    self.cards.append({"number": i + 1, "suit": j})

    def shuffle(self):
        random.shuffle(self.cards)
        random.shuffle(self.cards)
        random.shuffle(self.cards)  # shuffling 3 times to ensure resources

    def draw(self, amount):
        if amount > len(self.cards):
            raise IndexError
        if amount == 1:
            drawn_card = self.cards.pop(0)
            return drawn_card
        else:
            drawn_cards = self.cards[:amount]
            for i in drawn_cards:
                self.cards.remove(i)
            return drawn_cards
