# game.py - файл до рефакторинга

import random

class Game:
    def __init__(self):
        self.score = 0
        self.attempts = 0
        self.max_attempts = 0
        self.secret_number = 0
        self.difficulty = ""
    
    def start(self):
        print("Добро пожаловать в игру 'Угадай число'!")
        self.select_difficulty()
        self.setup_game()
        self.play()
    
    def select_difficulty(self):
        print("Выберите сложность:")
        print("1. Легкая (1-10, 5 попыток)")
        print("2. Средняя (1-50, 7 попыток)")
        print("3. Сложная (1-100, 10 попыток)")
        
        choice = input("Ваш выбор (1-3): ")
        
        if choice == "1":
            self.difficulty = "easy"
            self.max_attempts = 5
        elif choice == "2":
            self.difficulty = "medium"
            self.max_attempts = 7
        elif choice == "3":
            self.difficulty = "hard"
            self.max_attempts = 10
        else:
            print("Неверный выбор, установлена средняя сложность")
            self.difficulty = "medium"
            self.max_attempts = 7
    
    def setup_game(self):
        if self.difficulty == "easy":
            self.secret_number = random.randint(1, 10)
        elif self.difficulty == "medium":
            self.secret_number = random.randint(1, 50)
        elif self.difficulty == "hard":
            self.secret_number = random.randint(1, 100)
        
        print(f"Игра началась! У вас {self.max_attempts} попыток.")
    
    def play(self):
        while self.attempts < self.max_attempts:
            try:
                guess = int(input(f"Попытка {self.attempts + 1}. Введите число: "))
                
                if guess < self.secret_number:
                    print("Слишком маленькое!")
                elif guess > self.secret_number:
                    print("Слишком большое!")
                else:
                    print(f"Поздравляем! Вы угадали число {self.secret_number}!")
                    self.score += (self.max_attempts - self.attempts) * 10
                    break
                
                self.attempts += 1
                
                if self.attempts == self.max_attempts:
                    print(f"Попытки закончились! Загаданное число было: {self.secret_number}")
            
            except ValueError:
                print("Пожалуйста, введите целое число!")
        
        self.show_results()
    
    def show_results(self):
        print(f"\n--- Результаты ---")
        print(f"Сложность: {self.difficulty}")
        print(f"Загаданное число: {self.secret_number}")
        print(f"Использовано попыток: {self.attempts}")
        print(f"Счет: {self.score}")
        
        if self.attempts < self.max_attempts:
            print("Статус: Победа!")
        else:
            print("Статус: Поражение")

class HighScoreManager:
    def __init__(self):
        self.scores = []
    
    def add_score(self, player_name, score, difficulty):
        self.scores.append({
            'name': player_name,
            'score': score,
            'difficulty': difficulty
        })
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]  # Только топ-10
    
    def show_high_scores(self):
        print("\n=== Таблица рекордов ===")
        if not self.scores:
            print("Пока нет рекордов!")
            return
        
        for i, score in enumerate(self.scores, 1):
            print(f"{i}. {score['name']} - {score['score']} ({score['difficulty']})")

def main_menu():
    high_score_manager = HighScoreManager()
    
    while True:
        print("\n=== ГЛАВНОЕ МЕНЮ ===")
        print("1. Начать новую игру")
        print("2. Показать таблицу рекордов")
        print("3. Выход")
        
        choice = input("Выберите опцию: ")
        
        if choice == "1":
            game = Game()
            game.start()
            
            name = input("Введите ваше имя для таблицы рекордов: ")
            if name:
                high_score_manager.add_score(name, game.score, game.difficulty)
        
        elif choice == "2":
            high_score_manager.show_high_scores()
        
        elif choice == "3":
            print("Спасибо за игру!")
            break
        
        else:
            print("Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main_menu()
