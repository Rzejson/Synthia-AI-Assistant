def log_interaction(func):
    def wrapper(*args, **kwargs):
        print('--- NOWA INTERAKCJA ---')
        result = func(*args, **kwargs)
        print('--- KONIEC INTERAKCJI ---')
        return result
    return wrapper


@log_interaction
def send_message():
    print('Wysyłam wiadomość...')


class Conversation:
    def __init__(self):
        self.messages = []

    @log_interaction
    def add_message(self, content, author):
        self.messages.append({'author': author, 'content': content})

    def view_history(self):
        return '\n'.join(f'{element["author"]}: {element["content"]}' for element in self.messages)


if __name__ == "__main__":
    moj_czat = Conversation()

    moj_czat.add_message("Cześć, jak się masz?", "user")
    moj_czat.add_message("Witaj! Jestem systemem AI, w czym mogę pomóc?", "assistant")

    historia = moj_czat.view_history()
    print(historia)
