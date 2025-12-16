class GameState:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.score = 0
        self.attempts = 0
        self.secret_number = 0
        self.game_over = False
        self.won = False
    
    def increment_attempts(self):
        self.attempts += 1
    
    def calculate_score(self):
        remaining_attempts = self.difficulty.max_attempts - self.attempts
        self.score = remaining_attempts * self.difficulty.score_multiplier
        return self.score
    
    def is_max_attempts_reached(self):
        return self.attempts >= self.difficulty.max_attempts
    
    def check_win_condition(self, guess):
        if guess == self.secret_number:
            self.won = True
            self.game_over = True
            return True
        return False
    
    def get_hint(self, guess):
        if guess < self.secret_number:
            return "Слишком маленькое!"
        else:
            return "Слишком большое!"
