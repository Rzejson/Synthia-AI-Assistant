from core import Conversation


def test_add_message():
    # Arrange
    chat_test = Conversation()
    # Act
    chat_test.add_message("I'm Syntia, your personal AI assistant, and this is a test message.", 'Synthia')
    # Assert
    assert len(chat_test.messages) == 1
    assert chat_test.messages[0]['author'] == 'Synthia'
    assert chat_test.messages[0]['content'] == "I'm Syntia, your personal AI assistant, and this is a test message."


def test_view_history_formatting():
    chat_test = Conversation()
    chat_test.add_message("I'm Syntia, your personal AI assistant and this is a test message.", 'Synthia')
    chat_test.add_message("Ok. Understood.", 'User')
    history_test = chat_test.view_history()
    expected_record = "Synthia: I'm Syntia, your personal AI assistant and this is a test message.\n" \
                      "User: Ok. Understood."
    assert history_test == expected_record
