import random
import numpy as np

INF = float('inf')

class WhiteElephant:
    def __init__(self, n, sl_g=INF, sl_p=INF, sl_r=3, sl_f=INF, fs=True):
        # the number of players (and gifts) in the game
        self.n = n

        # whether or not the first player may swap gifts at the end
        self.final_swap = fs

        # the number of times per game a single gift can be stolen
        self.gift_steal_limit = sl_g

        # the number of times per game a single player can be stolen from
        self.player_steal_limit = sl_p

        # the number of times gifts can be stolen within a given round
        self.round_steal_limit = sl_r

        # the number of swaps that can occur during the final swap (if active)
        self.final_swap_limit = sl_f

        # a nxn matrix V of values
        # v = V[i][j] means player i considers gift j to be of value v
        self.gift_values = []
        # for now, assume each gift has a distinct integer value in [1, n]
        # and that values are the same for all players
        row = list(range(1, self.n+1))
        random.shuffle(row)
        for i in range(self.n):
            self.gift_values.append(row)

        # finish initialization
        self.reset()

    # Resets the game to play again.
    # Number of players and gift values does not change
    def reset(self):
        # the gift (an index) each player is currently holding
        self.player_gifts = [None]*self.n

        # the number of times each player has been stolen from
        self.player_stolen_counts = [0]*self.n

        # the number of times each gift has been stolen
        self.gift_stolen_counts = [0]*self.n

        # whether or not each gift has been unwrapped or stolen this round
        self.gift_active_this_round = [False]*self.n

        # a nxn matrix R of ranks
        # r = R[i][j] means player i considers gift j to be
        #   better than r-1 of the other opened gifts
        #   (r = None for unopened gift)
        # this could be calculated from other state but efficiency
        self.gift_ranks = []
        for i in range(self.n):
            self.gift_ranks.append([None]*self.n)

        # the number of gifts already opened
        self.m = 0

    # expected final rank of the gift
    # assumes unopened gifts have random rank regardless of opened gifts
    def efr(self, r):
        return r*(1 + (self.n-self.m)/(self.m+1))

    # returns an iterable of all (player, gifts) which may be stolen
    def get_stealable_gifts(self):
        def filter_fn(pg):
            p, g = pg
            if g == None:
                return False
            return not (
                self.gift_active_this_round[g] or 
                self.gift_stolen_counts[g] >= self.gift_steal_limit or
                self.player_stolen_counts[p] >= self.player_steal_limit
            )
        return filter(filter_fn, enumerate(self.player_gifts))

    # finds the open and stealable gift with the highest rank for a given player
    def find_best_gift(self, player):
        best_player = None
        best_gift = None
        best_rank = 0
        for player, gift in self.get_stealable_gifts():
            rank = self.gift_ranks[player][gift]
            if rank > best_rank:
                best_player = player
                best_gift = gift
                best_rank = rank
        return best_player, best_gift, best_rank

    # run a single turn of white elephant (player gets to go)
    def do_turn(self, player):
        if sum(self.gift_active_this_round) < self.round_steal_limit:
            best_player, best_gift, best_rank = self.find_best_gift(player)
            if best_player != None:
                best_efr = self.efr(best_rank)
                if best_efr > self.n/2:
                    self.steal(player, best_player)
                    self.do_turn(best_player)
                    return
        self.open(player)

    def do_round(self):
        self.do_turn(self.m)
        for i in range(self.n):
            self.gift_active_this_round[i] = False

    def do_final_swap(self, player):
        best_player, best_gift, best_rank = self.find_best_gift(player)
        if best_rank > self.gift_ranks[player][self.player_gifts[player]]:
            self.swap(player, best_player)
            self.do_final_swap(best_player)

    # run white elephant for n turns
    def do_game(self):
        for i in range(self.n):
            self.do_round()
        if self.final_swap:
            self.do_final_swap(0)

    # open the next gift and give it to player
    def open(self, player):
        gift = self.m
        # update rankings of gifts
        for p in range(self.n):
            opened_gift_rank = 0
            for g in range(self.m):
                if self.gift_values[p][g] >= self.gift_values[p][gift]:
                    self.gift_ranks[p][g] += 1
                else:
                    opened_gift_rank += 1
            self.gift_ranks[p][gift] = opened_gift_rank
        # assign now opened gift to player
        self.player_gifts[player] = gift
        self.gift_active_this_round[gift] = True
        self.m += 1

    # have the thief steal from the victim
    def steal(self, thief, victim):
        gift = self.player_gifts[victim]
        self.player_gifts[thief] = gift
        self.player_gifts[victim] = None
        self.player_stolen_counts[victim] += 1
        self.gift_stolen_counts[gift] += 1
        self.gift_active_this_round[gift] = True

    def swap(self, player1, player2):
        gift1 = self.player_gifts[player1]
        gift2 = self.player_gifts[player2]
        self.player_gifts[player1] = gift2
        self.player_gifts[player2] = gift1
        self.gift_active_this_round[gift1] = True
        self.gift_active_this_round[gift2] = True

nplayers = 10
ntrials = 10000
avg = np.zeros(nplayers)
for i in range(ntrials):
    we = WhiteElephant(10, sl_r=INF)
    we.do_game()
    val = [we.gift_values[p][g] for p, g in enumerate(we.player_gifts)]
    avg += ntrials**-1 * np.array(val)
print(avg)