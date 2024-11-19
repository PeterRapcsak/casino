import random
import json
import os

szin = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
nev = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
ertekek = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 7, '7': 7, '8': 8, '9': 9, '10': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}

deck = [{'ertek': ertek, 'suit': suit, 'value': ertekek[ertek]} for ertek in nev for suit in szin] * 4

random.shuffle(deck)

DATA = "data.json"
INITIAL_BALANCE = 100

if not os.path.exists(DATA):
    with open(DATA, 'w') as f:
        json.dump({}, f)

def load_balance(name):
    try:
        with open(DATA, 'r') as f:
            balances = json.load(f)
    except json.JSONDecodeError:
        balances = {}
        with open(DATA, 'w') as f:
            json.dump(balances, f)

    if name not in balances:
        print(f"No record found for {name}. Creating a new account with ${INITIAL_BALANCE}.")
        balances[name] = INITIAL_BALANCE
        with open(DATA, 'w') as f:
            json.dump(balances, f)

    return balances[name]

def save_balance(name, balance):
    try:
        with open(DATA, 'r') as f:
            balances = json.load(f)
    except json.JSONDecodeError:
        balances = {}
    balances[name] = balance
    with open(DATA, 'w') as f:
        json.dump(balances, f)

def calculate_hand_value(hand):
    value = sum(card['value'] for card in hand)
    aces = sum(1 for card in hand if card['ertek'] == 'Ace')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(hand, name="Player"):
    hand_str = ', '.join(f"{card['ertek']} of {card['suit']}" for card in hand)
    print(f"{name}: {hand_str} (Value: {calculate_hand_value(hand)})")

def blackjack(player_name, balance):
    global deck
    if len(deck) < 20:
        print("Reshuffling deck...")
        deck = [{'ertek': ertek, 'suit': suit, 'value': ertekek[ertek]} for ertek in nev for suit in szin] * 4
        random.shuffle(deck)

    # Refill balance if it's 0
    if balance <= 0:
        balance = INITIAL_BALANCE
        save_balance(player_name, balance)

    print(f"Your current balance: ${balance}")
    bet = 0
    while True:
        try:
            bet = int(input("Place your bet: $"))
            if bet > balance:
                print("You don't have enough balance!")
            elif bet <= 0:
                print("Bet must be a positive amount!")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    display_hand(player_hand, player_name)
    print(f"Dealer: {dealer_hand[0]['ertek']} of {dealer_hand[0]['suit']}, [Hidden]")

    # Immediate win if player gets a Blackjack
    if calculate_hand_value(player_hand) == 21:
        print("Blackjack! You win!")
        balance += int(bet * 1.5)  # Blackjack pays 3:2
        save_balance(player_name, balance)
        print(f"Your current balance is ${balance}.")
        return balance

    # Player's turn
    while True:
        player_value = calculate_hand_value(player_hand)
        if player_value > 21:
            print("Player busts! You lose.")
            balance -= bet
            save_balance(player_name, balance)
            print(f"Your current balance is ${balance}.")
            return balance
        print("Options: (H)it, (S)tand, (D)ouble")
        choice = input("").strip().upper()
        if choice == 'H':
            player_hand.append(deck.pop())
            display_hand(player_hand, player_name)
        elif choice == 'S':
            break
        elif choice == 'D':
            if len(player_hand) == 2:
                if bet * 2 > balance:
                    print("You don't have enough balance to double down!")
                else:
                    bet *= 2
                    player_hand.append(deck.pop())
                    display_hand(player_hand, player_name)
                    break
            else:
                print("You can only double on your first turn.")
        else:
            print("Invalid choice.")

    # Dealer's turn
    print("Dealer's turn...")
    display_hand(dealer_hand, "Dealer")
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
        display_hand(dealer_hand, "Dealer")

    dealer_value = calculate_hand_value(dealer_hand)
    player_value = calculate_hand_value(player_hand)

    # Determine the winner
    if dealer_value > 21 or player_value > dealer_value:
        print("You win!")
        balance += bet
    elif player_value < dealer_value:
        print("Dealer wins. You lose.")
        balance -= bet
    else:
        print("It's a tie!")
    save_balance(player_name, balance)
    print(f"Your current balance is ${balance}.")
    return balance

if __name__ == "__main__":
    print("Welcome to Blackjack!")
    player_name = input("Enter your name: ").strip()
    balance = load_balance(player_name)
    print(f"Welcome, {player_name}!")

    while True:
        balance = blackjack(player_name, balance)
        if balance <= 0:
            print("You ran out of money! Game over.")
            break
        again = input("Play again? (Y/N): ").strip().upper()
        if again != 'Y':
            break
    print(f"Goodbye, {player_name}! Your final balance is ${balance}.")
