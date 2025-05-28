
import random
import os
import colorama
from colorama import Fore, Style
from collections import deque
from datetime import datetime


colorama.init(autoreset=True)
import re
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')  # reset / kolory itp.

def pad_visible(s: str, width: int) -> str:
    vis_len = len(ANSI_RE.sub('', s))
    return s + ' ' * max(0, width - vis_len)




#GLOBALNE KONSTANTY
SUITS = ['♥', '♦', '♠', '♣']  # Kier, Karo, Pik, Trefl
VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

RED_SUITS = {'♥', '♦'}
BLACK_SUITS = {'♠', '♣'}

EASY_MODE = 1
HARD_MODE = 3
RANKING_FILE = "ranking.txt"

class Card:
    def __init__(self, value, suit, face_up=False):
        self.value = value
        self.suit = suit
        self.face_up = face_up
        self.highlighted = False

    def __str__(self):
        if not self.face_up:
            border_color = Fore.GREEN if self.highlighted else ""
            reset = Style.RESET_ALL if self.highlighted else ""
            return "\n".join([
                f"{border_color}┌───────┐{reset}",
                f"{border_color}│░░░░░░░│{reset}",
                f"{border_color}│░░ X ░░│{reset}",
                f"{border_color}│░░░░░░░│{reset}",
                f"{border_color}└───────┘{reset}"
            ])

        raw_val   = f"{self.value}{self.suit}"
        color     = Fore.RED if self.is_red() else Fore.WHITE
        vis_val   = f"{color}{raw_val}{Style.RESET_ALL}"
        vis_suit  = f"{color}{self.suit}{Style.RESET_ALL}"

        border_color = Fore.GREEN if self.highlighted else ""
        reset = Style.RESET_ALL if self.highlighted else ""

        top    = f"│{raw_val:<7}│".replace(raw_val, vis_val)
        center = f"│   {self.suit}   │".replace(self.suit, vis_suit)
        bot    = f"│{raw_val:>7}│".replace(raw_val, vis_val)

        return "\n".join([
            f"{border_color}┌───────┐{reset}",
            f"{border_color}{top}{reset}",
            f"{border_color}{center}{reset}",
            f"{border_color}{bot}{reset}",
            f"{border_color}└───────┘{reset}"
        ])



    def is_red(self):
        return self.suit in RED_SUITS

    def is_black(self):
        return self.suit in BLACK_SUITS

    def get_numeric_value(self):
        return VALUES.index(self.value) + 1

# tasuje talie i tworzy 52 karty
def generate_deck():
    return [Card(value, suit) for suit in SUITS for value in VALUES]

# czyści ekran
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# zapisuje wynik do pliku
def zapisz_do_rankingu(wynik):
    with open(RANKING_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {wynik}\n")

# Główna logika gry
class Solitaire:
    def __init__(self, difficulty=EASY_MODE):
        self.deck = generate_deck()
        random.shuffle(self.deck)
        self.columns = [[] for _ in range(7)]
        self.foundation = {suit: [] for suit in SUITS}
        self.waste = []
        self.stock = deque()
        self.difficulty = difficulty
        self.history = []
        self.move_counter = 0
        self.setup_game()

    # rozdaje karty na początek gry
    def setup_game(self):
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop(0)
                card.face_up = j == i
                self.columns[i].append(card)
        self.stock.extend(self.deck)
        self.deck.clear()
        self.save_state()


    # dobiera karty ze stosu
    def draw_stock(self):
        if not self.stock and self.waste:
            self.stock = deque(reversed(self.waste))
            for c in self.stock:
                c.face_up = False
            self.waste.clear()
        drawn = []
        for _ in range(min(self.difficulty, len(self.stock))):
            card = self.stock.popleft()
            card.face_up = True
            drawn.append(card)
        self.waste.extend(drawn)
        self.save_state()

    # zaznacza kartę, którą da się ruszyć
    def highlight_hint(self):
        for col in self.columns:
            for card in col:
                card.highlighted = False
        if self.waste:
            self.waste[-1].highlighted = False

        for from_col in self.columns:
            if not from_col:
                continue
            card = from_col[-1]
            if not card.face_up:
                continue
            fstack = self.foundation[card.suit]
            expected = VALUES[len(fstack)] if fstack else 'A'
            if card.value == expected:
                card.highlighted = True
                return

        if self.waste:
            card = self.waste[-1]
            fstack = self.foundation[card.suit]
            expected = VALUES[len(fstack)] if fstack else 'A'
            if card.value == expected:
                card.highlighted = True
                return

        for from_idx, from_col in enumerate(self.columns):
            for i in range(len(from_col)):
                card = from_col[i]
                if not card.face_up:
                    continue
                segment = from_col[i:]
                for to_idx, to_col in enumerate(self.columns):
                    if from_idx == to_idx:
                        continue
                    if not to_col and card.value == 'K':
                        card.highlighted = True
                        return
                    if to_col and to_col[-1].face_up:
                        top_card = to_col[-1]
                        if card.get_numeric_value() + 1 == top_card.get_numeric_value():
                            if (card.is_red() and top_card.is_black()) or (card.is_black() and top_card.is_red()):
                                card.highlighted = True
                                return

        if self.waste:
            card = self.waste[-1]
            for to_col in self.columns:
                if not to_col:
                    if card.value == 'K':
                        card.highlighted = True
                        return
                else:
                    top_card = to_col[-1]
                    if top_card.face_up and top_card.get_numeric_value() == card.get_numeric_value() + 1:
                        if (top_card.is_red() and card.is_black()) or (top_card.is_black() and card.is_red()):
                            card.highlighted = True
                            return

        
    # zapisuje stan gry do historii (żeby działało cofanie)
    def save_state(self):
        import copy
        snapshot = {
            "columns": copy.deepcopy(self.columns),
            "foundation": copy.deepcopy(self.foundation),
            "waste": copy.deepcopy(self.waste),
            "stock": copy.deepcopy(self.stock),
            "move_counter": self.move_counter
        }
        self.history.append(snapshot)
        if len(self.history) > 3:
            self.history.pop(0)


    # przywraca poprzedni stan gry (undo)
    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            snapshot = self.history[-1]
            self.columns = snapshot["columns"]
            self.foundation = snapshot["foundation"]
            self.waste = snapshot["waste"]
            self.stock = snapshot["stock"]
            self.move_counter = snapshot["move_counter"]

    # przenosi kartę z kolumny do stosu końcowego (jeśli pasuje)
    def move_to_foundation(self, col_idx):
        col = self.columns[col_idx]
        if not col:
            return
        card = col[-1]
        foundation_stack = self.foundation[card.suit]
        expected_value = VALUES[len(foundation_stack)] if foundation_stack else 'A'
        if card.value == expected_value:
            foundation_stack.append(col.pop())
            self.move_counter += 1
            if col and not col[-1].face_up:
                col[-1].face_up = True
            self.save_state()


    # przenosi kartę z waste do stosu końcowego
    def move_waste_to_foundation(self):
        if not self.waste:
            return
        card = self.waste[-1]
        foundation_stack = self.foundation[card.suit]
        expected_value = VALUES[len(foundation_stack)] if foundation_stack else 'A'
        if card.value == expected_value:
            foundation_stack.append(self.waste.pop())
            self.move_counter += 1
            self.save_state()

    # przenosi całą część kolumny do innej kolumny
    def move_column_to_column(self, from_idx, to_idx):
        from_col = self.columns[from_idx]
        to_col = self.columns[to_idx]
        if not from_col:
            return

        if not to_col:
            for i in range(len(from_col)):
                if from_col[i].face_up and from_col[i].value == 'K':
                    self.columns[to_idx].extend(from_col[i:])
                    del from_col[i:]
                    if from_col and not from_col[-1].face_up:
                        from_col[-1].face_up = True
                    self.move_counter += 1
                    self.save_state()
                    return
            return

        top_card = to_col[-1]
        if not top_card.face_up:
            return

        for i in range(len(from_col)):
            moving_card = from_col[i]
            if not moving_card.face_up:
                continue
            if moving_card.get_numeric_value() + 1 == top_card.get_numeric_value():
                if (moving_card.is_red() and top_card.is_black()) or (moving_card.is_black() and top_card.is_red()):
                    self.columns[to_idx].extend(from_col[i:])
                    del from_col[i:]
                    if from_col and not from_col[-1].face_up:
                        from_col[-1].face_up = True
                    self.move_counter += 1
                    self.save_state()
                    return



    # przenosi kartę z waste do kolumny
    def move_waste_to_column(self, to_idx):
        if not self.waste:
            return
        card = self.waste[-1]
        to_col = self.columns[to_idx]
        if not to_col:
            if card.value == 'K':
                self.columns[to_idx].append(self.waste.pop())
                self.move_counter += 1
                self.save_state()
                return
        else:
            top_card = to_col[-1]
            if top_card.face_up and top_card.get_numeric_value() == card.get_numeric_value() + 1:
                if (top_card.is_red() and card.is_black()) or (top_card.is_black() and card.is_red()):
                    self.columns[to_idx].append(self.waste.pop())
                    self.move_counter += 1
                    self.save_state()

    # sprawdza czy wygrana (wszystkie stosy pełne)
    def check_win(self):
        return all(len(stack) == 13 for stack in self.foundation.values())

    # sprawdza czy przegrana (brak ruchów)
    def check_loss(self):
        if self.stock or self.waste:
            return False

        if self.waste:
            w = self.waste[-1]
            fstack = self.foundation[w.suit]
            expected = VALUES[len(fstack)] if fstack else 'A'
            if w.value == expected:
                return False
            for col in self.columns:
                if not col and w.value == 'K':
                    return False
                if col and col[-1].face_up and \
                col[-1].get_numeric_value() == w.get_numeric_value() + 1 and \
                ((col[-1].is_red() and w.is_black()) or (col[-1].is_black() and w.is_red())):
                    return False

        for i, from_col in enumerate(self.columns):
            if not from_col or not from_col[-1].face_up:
                continue
            c = from_col[-1]
            fstack = self.foundation[c.suit]
            expected = VALUES[len(fstack)] if fstack else 'A'
            if c.value == expected:
                return False
            for j, to_col in enumerate(self.columns):
                if i == j:
                    continue
                if not to_col:
                    if c.value == 'K':
                        return False
                else:
                    top = to_col[-1]
                    if top.face_up and top.get_numeric_value() == c.get_numeric_value() + 1 and \
                    ((top.is_red() and c.is_black()) or (top.is_black() and c.is_red())):
                        return False

        return True



    # rysuje całą planszę w terminalu
    def display(self):
        clear()
        card_height = 5
        max_col_height = max(len(col) for col in self.columns)

        lines = ["|" + "          |" * 7] * (max_col_height * card_height)
        for row in range(max_col_height):
            card_lines = [""] * card_height
            for col in self.columns:
                if row < len(col):
                    rendered = col[row].__str__().split("\n")
                else:
                    rendered = ["         "] * card_height
                for i in range(card_height):
                    card_lines[i] += rendered[i] + "  "
            for i in range(card_height):
                lines[row * card_height + i] = card_lines[i] + "|"

        # Panel boczny
        info_lines = []
        info_lines.append("=== PASJANS ===")
        info_lines.append(f"Ruchy: {self.move_counter}")
        info_lines.append("")
        info_lines.append("Stosy końcowe:")
        for suit in SUITS:
            stack = self.foundation[suit]
            top = stack[-1].__str__().split("\n")[1].strip() if stack else "---"
            info_lines.append(f"{suit}: {top}")
        info_lines.append("")
        info_lines.append(f"Stos rezerwowy:")
        info_lines.append(f"Odwrócone: {len(self.stock)}")
        if self.waste:
            info_lines.append("Widoczna karta:")
            info_lines.extend(self.waste[-1].__str__().split("\n"))
        else:
            info_lines.append("Widoczna karta: ---")

        i = 1
        print(' '+(''.join(f'------{i}----' for i in range(1, 8))) + '-'*23)
        max_len = max(len(lines), len(info_lines))
        for i in range(max_len):
            left = lines[i] if i < len(lines) else ""
            right = info_lines[i] if i < len(info_lines) else ""
            row_number = (i // 5) + 1 if i % 5 == 2 else " ᱾"
            row_label = f"{row_number:<2} " if row_number else "   "

            print(f"{row_label}{pad_visible(left, 80)} {right}")

        for col in self.columns:
            for card in col:
                if isinstance(card.value, str) and '\x1b[' in card.value:
                    for val in VALUES:
                        if val in card.value:
                            card.value = val
                            break
    

        print('-' * 100)
        
    # główna pętla gry i obsługa komend
    def run(self):
        while True:
            self.display()
            for col in self.columns:
                for card in col:
                    card.highlighted = False

            if self.check_win():
                print("\nGRATULACJE! Ułożyłeś pasjansa w", self.move_counter, "ruchach!")
                zapisz_do_rankingu(f"WYGRANA w {self.move_counter} ruchach")
                break
            if self.check_loss():
                print("\nPRZEGRANA! Brak możliwych ruchów.")
                zapisz_do_rankingu(f"PRZEGRANA po {self.move_counter} ruchach")
                break
            print("\nKomendy: d - dobierz | u - undo | h - podpowiedż | m X Y - przenieś kolumnę | f X - do stosu końcowego | w Y - waste do kolumny | wf - waste do stosu końcowego | q - wyjdź")
            cmd = input("> ").strip().lower().split()
            if not cmd:
                continue
            if cmd[0] == 'd':
                self.draw_stock()
                self.move_counter += 1
            elif cmd[0] == 'u':
                self.undo()
            elif cmd[0] == 'q':
                break
            elif cmd[0] == 'f' and len(cmd) == 2 and cmd[1].isdigit():
                self.move_to_foundation(int(cmd[1]) - 1)
            elif cmd[0] == 'm' and len(cmd) == 3 and cmd[1].isdigit() and cmd[2].isdigit():
                self.move_column_to_column(int(cmd[1]) - 1, int(cmd[2]) - 1)
            elif cmd[0] == 'w' and len(cmd) == 2 and cmd[1].isdigit():
                self.move_waste_to_column(int(cmd[1]) - 1)
            elif cmd[0] == 'wf':
                self.move_waste_to_foundation()
            elif cmd[0] == 'h':
                self.highlight_hint()
    

# Uruchomienie gry
if __name__ == '__main__':
    print("Wybierz poziom trudności: 1 - łatwy (1 karta), 3 - trudny (3 karty)")
    level = input("> ").strip()
    level = EASY_MODE if level == '1' else HARD_MODE
    game = Solitaire(difficulty=level)
    game.run()