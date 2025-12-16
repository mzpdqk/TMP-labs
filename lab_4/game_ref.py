import random
from difficulty import Difficulty
from game_state import GameState
from input_handler import InputHandler

class Game:
    def __init__(self):
        self.state = None
        self.difficulty = None
    
    def start(self):
        print("Добро пожаловать в игру 'Угадай число'!")
        self._select_difficulty()
        self._setup_game()
        self._play()
    
    def _select_difficulty(self):
        print("Выберите сложность:")
        print("1. Легкая (1-10, 5 попыток)")
        print("2. Средняя (1-50, 7 попыток)")
        print("3. Сложная (1-100, 10 попыток)")
        
        choice = InputHandler.get_menu_choice("Ваш выбор (1-3): ", ["1", "2", "3"])
        
        if choice == "1":
            level = "easy"
        elif choice == "2":
            level = "medium"
        else:
            level = "hard"
        
        self.difficulty = Difficulty.create_difficulty(level)
    
    def _setup_game(self):
        self.state = GameState(self.difficulty)
        self.state.secret_number = random.randint(
            self.difficulty.min_num, 
            self.difficulty.max_num
        )
        print(f"Игра началась! У вас {self.difficulty.max_attempts} попыток.")
    
    def _play(self):
        while not self.state.game_over:
            self._process_turn()
        
        self._show_results()
    
    def _process_turn(self):
        guess = InputHandler.get_integer_input(
            f"Попытка {self.state.attempts + 1}. Введите число: "
        )
        
        if self.state.check_win_condition(guess):
            print(f"Поздравляем! Вы угадали число {self.state.secret_number}!")
            self.state.calculate_score()
        else:
            print(self.state.get_hint(guess))
            self.state.increment_attempts()
            
            if self.state.is_max_attempts_reached():
                print(f"Попытки закончились! Загаданное число было: {self.state.secret_number}")
                self.state.game_over = True
    
    def _show_results(self):
        print(f"\n--- Результаты ---")
        print(f"Сложность: {self.difficulty.name}")
        print(f"Загаданное число: {self.state.secret_number}")
        print(f"Использовано попыток: {self.state.attempts}")
        print(f"Счет: {self.state.score}")
        
        if self.state.won:
            print("Статус: Победа!")
        else:
            print("Статус: Поражение")
    
    @property
    def score(self):
        return self.state.score if self.state else 0
    
    @property
    def difficulty_level(self):
        return self.difficulty.name.lower() if self.difficulty else ""
