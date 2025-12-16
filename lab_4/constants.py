class GameConstants:
    EASY_CONFIG = {
        'range': (1, 10),
        'attempts': 5,
        'multiplier': 10
    }
    
    MEDIUM_CONFIG = {
        'range': (1, 50),
        'attempts': 7,
        'multiplier': 15
    }
    
    HARD_CONFIG = {
        'range': (1, 100),
        'attempts': 10,
        'multiplier': 20
    }
    
    DIFFICULTY_MAP = {
        '1': ('easy', EASY_CONFIG),
        '2': ('medium', MEDIUM_CONFIG),
        '3': ('hard', HARD_CONFIG)
    }
