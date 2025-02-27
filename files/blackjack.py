import json
from io import BytesIO

import discord

from files.modules.combine_images import combine_images
from files.objects import user, deck


class Player(discord.ui.View):
    def __init__(self, user, bet: int, bal: int, cards: list,
                 deck: deck.Deck):  # making user object for easier data handling
        super().__init__()
        self.user = user
        self.bet = bet
        self.bal = bal
        self.cards = cards
        self.deck = deck
        self.value = 0

    def value_check(self):
        self.value = 0
        for j in self.cards:
            if j['number'] > 10:
                a = 10
            else:
                a = j['number']
            self.value += a

    # different function to control cards, bets, and check for balance
    @discord.ui.button(label='Hit', style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        card = self.deck.draw(1)
        if card['number'] > 10:
            a = 10
        else:
            a = card['number']
        self.value_check()
        if self.value + a > 21:
            await interaction.response.send_message(f"You already lost", ephemeral=True)
            return
        card_img = f"{card['number']}_of_{card['suit']}.png"
        self.cards.append(card)
        await interaction.response.send_message(f"You drawn:", file=discord.File(f"./resources/cards_faces/{card_img}",
                                                                                 filename=card_img), ephemeral=True)

    @discord.ui.button(label='Double Down', style=discord.ButtonStyle.gray)
    async def double_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bet > self.bal:
            interaction.response.send_message(f"You don't have enough money", ephemeral=True)
            return
        card = self.deck.draw(1)
        if card['number'] > 10:
            a = 10
        else:
            a = card['number']
        self.value_check()
        if self.value + a > 21:
            await interaction.response.send_message(f"You already lost", ephemeral=True)
            return
        self.bet += self.bet
        self.cards.append(card)
        card_img = f"{card['number']}_of_{card['suit']}.png"
        await interaction.response.send_message(f"You drawn:", file=discord.File(f"./resources/cards_faces/{card_img}",
                                                                                 filename=card_img), ephemeral=True)


class Turns(discord.ui.View):
    def __init__(self, current_turn: Player, players, turn_num):
        super().__init__()
        self.current_turn = current_turn
        self.players = players
        self.turn_num = turn_num

    @discord.ui.button(label='Show card', style=discord.ButtonStyle.green)
    async def start_turn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.current_turn.user.id:
            await interaction.response.send_message(f"This is not your turn", ephemeral=True)
            return
        cards = []
        for i in self.current_turn.cards:
            card = f"./resources/cards_faces/{i['number']}_of_{i['suit']}.png"
            cards.append(card)
        dest = BytesIO()
        combine_images(cards, dest)
        dest.seek(0)
        view = self.current_turn
        await interaction.response.send_message(file=discord.File(dest, filename=f"cards.png"), view=view,
                                                ephemeral=True)
        return

    @discord.ui.button(label='End Turn', style=discord.ButtonStyle.red)
    async def end_turn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.turn_num += 1
        if self.turn_num >= len(self.players):
            result = ""
            prize_pool = 0
            out_players = sorted(self.players, key=lambda player: abs(21 - player.value))
            for i in out_players:
                prize_pool += i.bet
                if i.value >= 22:
                    out_players.remove(i)
                    out_players.append(i)
            for i in out_players:
                if out_players.index(i) == 0:
                    winning = round(2 / 3 * prize_pool, 2)
                elif out_players.index(i) == 1:
                    winning = round(prize_pool / 3, 2)
                else:
                    winning = 0
                i.bal += winning
                with open("resources/user_list.json", "r+") as outfile:
                    data = json.load(outfile)
                    data[str(i.user.id)]["balance"] = i.bal
                    outfile.seek(0)
                    json.dump(data, outfile, indent=4)
                    outfile.close()
                i.value_check()
                result += f"{i.user.mention} have score of: {i.value}; and have won: {winning}\n"
            embed = discord.Embed(title="Result", description=result, color=discord.Color.green())
            await interaction.response.send_message(content=f"Game ended", embed=embed)
            return
        if interaction.user.id != self.current_turn.user.id:
            await interaction.response.send_message(f"This is not your turn", ephemeral=True)
            return
        embed = discord.Embed(title="BlackJack", color=discord.Color.blue(),
                              description=f"It is {self.players[self.turn_num].user.mention} turn")
        view = Turns(self.players[self.turn_num], self.players, self.turn_num)
        await interaction.response.send_message(embed=embed, view=view)
        return


class Blackjack:  # blackjack obj where the game will be played
    def __init__(self, deck):
        self.players = {}
        self.deck = deck
        self.deck.shuffle()

    async def start(self, interaction: discord.Interaction):
        players = list(self.players.values())
        for i in self.players.values():
            i.cards = self.deck.draw(2)
        embed = discord.Embed(title="BlackJack", color=discord.Color.blue(),
                              description=f"It is {players[0].user.mention} turn")
        view = Turns(players[0], players, 0)
        await interaction.response.send_message(embed=embed, view=view)


class PlaceBet(discord.ui.Modal):  # modal pop up to get the amount the player want to bet
    def __init__(self, blackjack, user_dict):
        super().__init__(title="Amount you want to bet")
        self.blackjack = blackjack
        self.user_dict = user_dict

    amount = discord.ui.TextInput(
        label='Amount',
        placeholder='Amount to bet',
    )

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id not in self.user_dict:
            new_user = {
                "id": interaction.user.id,
                "balance": 1000,
            }
            with open("resources/user_list.json", "r+") as outfile:
                data = json.load(outfile)
                data[str(interaction.user.id)] = new_user
                outfile.seek(0)
                json.dump(data, outfile, indent=4)
                outfile.close()
            self.user_dict[interaction.user.id] = user.User(interaction.user.id)
        try:
            if int(self.amount.value) > int(self.user_dict[
                                                interaction.user.id].balance):  # make sure the input is valid type and does not exceed player balance
                await interaction.response.send_message(f'Invalid Amount!', ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message(f'Invalid Amount!', ephemeral=True)
            return
        player = Player(user=interaction.user, bet=int(self.amount.value),
                        bal=self.user_dict[interaction.user.id].balance, deck=self.blackjack.deck,
                        cards=self.blackjack.deck.draw(2))
        player.bal -= int(self.amount.value)
        self.blackjack.players[interaction.user.id] = player
        await interaction.response.send_message(f'You have placed {self.amount.value} coins as bet.', ephemeral=True)


class BlackjackView(discord.ui.View):
    def __init__(self, user_dict):
        super().__init__()
        self.blackjack = Blackjack(deck.Deck(1))
        self.user_dict = user_dict

    @discord.ui.button(label='join', style=discord.ButtonStyle.gray)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.blackjack.players:
            await interaction.response.send_message(f'Don\'t be greedy',
                                                    ephemeral=True)
            return
        if interaction.user.id not in self.user_dict:
            new_user = {
                "id": interaction.user.id,
                "balance": 1000,
            }
            with open("resources/user_list.json", "r+") as outfile:
                data = json.load(outfile)
                data[interaction.user.id] = new_user
                outfile.seek(0)
                json.dump(data, outfile, indent=4)
            self.user_dict[interaction.user.id] = user.User(interaction.user.id)
        await interaction.response.send_modal(PlaceBet(self.blackjack, self.user_dict))

    @discord.ui.button(label='start', style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.blackjack.start(interaction)
        print(self.blackjack.players[interaction.user.id].user.name)
