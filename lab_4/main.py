from game_ref import Game
from score_manager import HighScoreManager

class GameFactory:
    @staticmethod
    def create_game():
        return Game()
    
    @staticmethod
    def create_high_score_manager(filename="highscores.txt"):
        return HighScoreManager(filename)

class GameMenu:
    def __init__(self):
        self.factory = GameFactory()
        self.high_score_manager = self.factory.create_high_score_manager()
        self.running = True
    
    def run(self):
        while self.running:
            self._show_menu()
            self._handle_choice()
    
    def _show_menu(self):
        print("\n=== ГЛАВНОЕ МЕНЮ ===")
        print("1. Начать новую игру")
        print("2. Показать таблицу рекордов (по очкам)")
        print("3. Показать таблицу рекордов (по дате)")
        print("4. Показать таблицу рекордов (по сложности)")
        print("5. Выход")
    
    def _handle_choice(self):
        from input_handler import InputHandler
        
        choice = InputHandler.get_menu_choice(
            "Выберите опцию: ",
            ["1", "2", "3", "4", "5"]
        )
        
        if choice == "1":
            self._start_new_game()
        elif choice == "2":
            self.high_score_manager.show_high_scores("score")
        elif choice == "3":
            self.high_score_manager.show_high_scores("date")
        elif choice == "4":
            self.high_score_manager.show_high_scores("difficulty")
        elif choice == "5":
            self._exit_game()
    
    def _start_new_game(self):
        game = self.factory.create_game()
        game.start()
        
        from input_handler import InputHandler
        name = InputHandler.get_non_empty_string("Введите ваше имя для таблицы рекордов: ")
        
        if name:
            self.high_score_manager.add_score(name, game.score, game.difficulty_level)
    
    def _exit_game(self):
        print("Спасибо за игру!")
        self.running = False

def main():
    menu = GameMenu()
    menu.run()

if __name__ == "__main__":
    main()
