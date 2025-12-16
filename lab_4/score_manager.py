from dataclasses import dataclass
from typing import List, Protocol
from datetime import datetime

@dataclass
class ScoreEntry:
    name: str
    score: int
    difficulty: str
    date: datetime
    
    def __str__(self):
        return f"{self.name} - {self.score} ({self.difficulty}) - {self.date.strftime('%Y-%m-%d %H:%M')}"

class SortStrategy(Protocol):
    def sort(self, scores: List[ScoreEntry]) -> List[ScoreEntry]:
        pass

class ScoreSortStrategy:
    def sort(self, scores: List[ScoreEntry]) -> List[ScoreEntry]:
        return sorted(scores, key=lambda x: x.score, reverse=True)

class DateSortStrategy:
    def sort(self, scores: List[ScoreEntry]) -> List[ScoreEntry]:
        return sorted(scores, key=lambda x: x.date, reverse=True)

class DifficultySortStrategy:
    def sort(self, scores: List[ScoreEntry]) -> List[ScoreEntry]:
        return sorted(scores, key=lambda x: (x.difficulty, -x.score))

class HighScoreManager:
    def __init__(self, filename="highscores.txt", max_entries=10):
        self.filename = filename
        self.max_entries = max_entries
        self.scores: List[ScoreEntry] = []
        self.sort_strategy: SortStrategy = ScoreSortStrategy()
        self._load_scores()
    
    def set_sort_strategy(self, strategy: SortStrategy):
        self.sort_strategy = strategy
    
    def add_score(self, name: str, score: int, difficulty: str):
        entry = ScoreEntry(
            name=name,
            score=score,
            difficulty=difficulty,
            date=datetime.now()
        )
        self.scores.append(entry)
        self._save_scores()
    
    def _load_scores(self):
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        entry = ScoreEntry(
                            name=parts[0],
                            score=int(parts[1]),
                            difficulty=parts[2],
                            date=datetime.fromisoformat(parts[3])
                        )
                        self.scores.append(entry)
        except FileNotFoundError:
            pass
    
    def _save_scores(self):
        sorted_scores = self.sort_strategy.sort(self.scores)[:self.max_entries]
        with open(self.filename, 'w') as file:
            for entry in sorted_scores:
                file.write(f"{entry.name},{entry.score},{entry.difficulty},{entry.date.isoformat()}\n")
        self.scores = sorted_scores
    
    def show_high_scores(self, sort_by="score"):
        if not self.scores:
            print("\nТаблица рекордов пуста!")
            return
        
        if sort_by == "date":
            self.set_sort_strategy(DateSortStrategy())
        elif sort_by == "difficulty":
            self.set_sort_strategy(DifficultySortStrategy())
        else:
            self.set_sort_strategy(ScoreSortStrategy())
        
        print("\n=== Таблица рекордов ===")
        sorted_scores = self.sort_strategy.sort(self.scores)
        for i, entry in enumerate(sorted_scores[:10], 1):
            print(f"{i}. {entry}")
    
    def get_top_scores(self, n=5):
        return self.sort_strategy.sort(self.scores)[:n]
