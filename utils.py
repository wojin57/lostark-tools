from InquirerPy import inquirer

def ask_question(message, choices, default):
    answer = inquirer.select(
        message=message,
        choices=choices + ["종료"],
        default=default,
    ).execute()

    if answer == "종료":
        return None
    
    return answer
