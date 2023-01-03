from replit import clear
import random


def GameOver():
    print("You lose 😤")


def f_GameON():
    from art import logo
    print(logo)
    Game()


def Game():
    cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    player_total = []
    player_cards_num_1 = random.choice(cards)
    player_cards_num_2 = random.choice(cards)
    player_total.append(player_cards_num_1)
    player_total.append(player_cards_num_2)
    player_sum = player_cards_num_1 + player_cards_num_2
    print(f"Your cards: {player_total}, current score: {player_sum} ")
    GamePC(player_total, player_sum)


def GamePC(player_total, player_sum):
    cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    pc_total = []
    pc_card_num_1 = random.choice(cards)
    pc_total.append(pc_card_num_1)
    print(f"Computer's first card: {pc_total}:")
    GameFinalePlayer(pc_total, player_total, player_sum, pc_card_num_1)


def GameFinalePlayer(pc_total, player_total, player_sum, pc_card_num_1):
    finale = input("Type 'y' to get another card, type 'n' to pass:")
    if finale == "y":
        cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        player_cards_num_3 = random.choice(cards)
        player_total.append(player_cards_num_3)
        player_sum = player_sum + player_cards_num_3
        print(f"Your cards: {player_total}, current score: {player_sum}")
        print(f"Computer's first card: {pc_total}:")
        if player_sum > 21:
            GameOver()
        else:
            cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
            player_cards_num_4 = random.choice(cards)
            player_total.append(player_cards_num_4)
            player_sum = player_sum + player_cards_num_4
            return
    else:
        #This controls the last part of the game if the user input is 'n'. This means, the game ends.
        cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        pc_card_num_2 = random.choice(cards)
        pc_total.append(pc_card_num_2)
        pc_sum = pc_card_num_2 + pc_card_num_1
        if pc_sum < 17:
            pc_card_num_3 = random.choice(cards)
            pc_total.append(pc_card_num_3)
            PC_SUM = pc_sum + pc_card_num_3
        if pc_sum < 17:
            pc_card_num_4 = random.choice(cards)
            pc_total.append(pc_card_num_4)
            pc_end_sum = PC_SUM + pc_card_num_4
        else:
            pc_end_sum = pc_sum
        if pc_end_sum > 22 and player_sum < 22:
            print(f"Your cards: {player_total}, current score: {player_sum}")
            print(f"Computer's finale card: {pc_total}:")
            print("Congratz! You win!!")
        if pc_end_sum < 22 and player_sum > 22:
            print(f"Your cards: {player_total}, current score: {player_sum}")
            print(f"Computer's finale card: {pc_total}")
            print("You lose 😤")
        if pc_end_sum == player_sum:
            print(f"Your cards: {player_total}, current score: {player_sum}")
            print(f"Computer's finale card: {pc_total}:")
            print("DRAW!")

        #if player_sum >= 22:
        #print("You went over. You lose 😭")
    #Your cards: [8, 3, 4, 8], current score: 23
    #Computer's first card: 9
    #Your final hand: [8, 3, 4, 8], final score: 23
    #Computer's final hand: [9, 10], final score: 19


GameON = input("Do you want to play a game of Blackjack? Type 'y' or 'n':")
if GameON == "y":
    clear()
    f_GameON()
else:
    print("Why did you even start it!")
