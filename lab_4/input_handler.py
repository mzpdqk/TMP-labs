class InputHandler:
    @staticmethod
    def get_integer_input(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Пожалуйста, введите целое число!")
    
    @staticmethod
    def get_menu_choice(prompt, valid_choices):
        while True:
            choice = input(prompt)
            if choice in valid_choices:
                return choice
            print(f"Неверный выбор. Допустимые варианты: {', '.join(valid_choices)}")
    
    @staticmethod
    def get_non_empty_string(prompt):
        while True:
            name = input(prompt).strip()
            if name:
                return name
            print("Имя не может быть пустым!")
