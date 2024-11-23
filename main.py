import sys
import random
import json
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox, QMessageBox, QStackedWidget
from PySide6.QtCore import Qt

# Constants and Data Setup
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

class LoginScreen(QWidget):
    def __init__(self, app, stack):
        super().__init__()

        self.setWindowTitle('Blackjack - Login')
        self.setGeometry(100, 100, 400, 200)

        self.app = app
        self.stack = stack

        # UI Elements
        self.layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        self.layout.addWidget(self.name_input)

        self.start_button = QPushButton('Start Game', self)
        self.start_button.clicked.connect(self.start_game)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

    def start_game(self):
        self.player_name = self.name_input.text().strip()
        if not self.player_name:
            self.show_message("Error", "Name cannot be empty!")
            return
        
        self.balance = load_balance(self.player_name)

        # Switch to the game screen
        self.app.show_game_screen(self.player_name, self.balance)


    def show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


class GameScreen(QWidget):
    def __init__(self, app, player_name, balance):
        super().__init__()

        self.setWindowTitle('Blackjack - Game')
        self.setGeometry(100, 100, 400, 300)

        self.player_name = player_name
        self.balance = balance
        self.deck = [{'ertek': ertek, 'suit': suit, 'value': ertekek[ertek]} for ertek in nev for suit in szin] * 4
        random.shuffle(self.deck)

        # UI Elements
        self.layout = QVBoxLayout()

        self.balance_label = QLabel(f"Balance: ${self.balance}", self)
        self.layout.addWidget(self.balance_label)

        self.bet_label = QLabel('Place your bet: $', self)
        self.layout.addWidget(self.bet_label)

        self.bet_input = QSpinBox(self)
        self.bet_input.setRange(1, 1000)
        self.layout.addWidget(self.bet_input)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_game)
        self.layout.addWidget(self.play_button)

        self.result_label = QLabel('', self)
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)

    def play_game(self):
        bet = self.bet_input.value()
        if bet <= 0 or bet > self.balance:
            self.show_message("Error", "Invalid bet amount.")
            return
    
        # Deal initial hands
        player_hand = [self.deck.pop(), self.deck.pop()]
        dealer_hand = [self.deck.pop(), self.deck.pop()]
    
        self.display_hand(player_hand, "Player")
        self.result_label.setText(f"Dealer shows: {dealer_hand[0]['ertek']} of {dealer_hand[0]['suit']}")
    
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)
    
        # Immediate Blackjack check
        if player_value == 21:
            self.show_message("Blackjack", "Blackjack! You win!")
            self.balance += int(bet * 1.5)
            save_balance(self.player_name, self.balance)
            return
    
        while player_value < 21:
            self.result_label.setText("Options: Hit (H), Stand (S), Double (D)")
            choice = input().strip().upper()
    
            if choice == 'H':  # Hit
                player_hand.append(self.deck.pop())
                self.display_hand(player_hand, "Player")
                player_value = calculate_hand_value(player_hand)
            elif choice == 'S':  # Stand
                break
            elif choice == 'D' and len(player_hand) == 2:  # Double
                if bet * 2 <= self.balance:
                    bet *= 2
                    player_hand.append(self.deck.pop())
                    self.display_hand(player_hand, "Player")
                    break
                else:
                    self.show_message("Error", "Not enough balance to double!")
                    return
            else:
                self.show_message("Error", "Invalid choice. Please select again.")
                continue
            
        # Dealer's turn
        self.result_label.setText(f"Dealer's turn...{dealer_hand[1]['ertek']} of {dealer_hand[1]['suit']}")
        while dealer_value < 17:
            dealer_hand.append(self.deck.pop())
            dealer_value = calculate_hand_value(dealer_hand)
            self.display_hand(dealer_hand, "Dealer")
    
        # Determine winner
        if dealer_value > 21 or player_value > dealer_value:
            self.balance += bet
            self.show_message("You Win!", f"Your current balance is ${self.balance}.")
        elif player_value < dealer_value:
            self.balance -= bet
            self.show_message("You Lose", f"Your current balance is ${self.balance}.")
        else:
            self.show_message("Tie", "It's a tie!")
    
        save_balance(self.player_name, self.balance)


    def display_hand(self, hand, name="Player"):
        hand_str = ', '.join(f"{card['ertek']} of {card['suit']}" for card in hand)
        self.result_label.setText(f"{name}: {hand_str} (Value: {calculate_hand_value(hand)})")

    def show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


class BlackjackApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.stack = QStackedWidget()

        # Initialize screens
        self.login_screen = LoginScreen(self, self.stack)
        self.stack.addWidget(self.login_screen)

        self.setActiveScreen(self.login_screen)

    def setActiveScreen(self, screen):
        self.stack.setCurrentWidget(screen)
        self.stack.show()

    def show_game_screen(self, player_name, balance):
        game_screen = GameScreen(self, player_name, balance)
        self.stack.addWidget(game_screen)  # Add game screen to stack
        self.setActiveScreen(game_screen)  # Switch to the game screen


if __name__ == "__main__":
    app = BlackjackApp(sys.argv)
    sys.exit(app.exec())
