class Difficulty:
    def __init__(self, name, min_num, max_num, max_attempts, score_multiplier):
        self.name = name
        self.min_num = min_num
        self.max_num = max_num
        self.max_attempts = max_attempts
        self.score_multiplier = score_multiplier
    
    @staticmethod
    def create_difficulty(level):
        if level == "easy":
            return Difficulty("Легкая", 1, 10, 5, 10)
        elif level == "medium":
            return Difficulty("Средняя", 1, 50, 7, 15)
        elif level == "hard":
            return Difficulty("Сложная", 1, 100, 10, 20)
        return Difficulty("Средняя", 1, 50, 7, 15)
