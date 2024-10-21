import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

class CommandProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def get_wordnet_pos(self, word):
        """Map POS tag to first character lemmatize() accepts."""
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def preprocess_command(self, command):
        """Preprocess the command text: tokenize, lemmatize, and return cleaned words."""
        tokens = word_tokenize(command.lower())  # Tokenize and lowercase the input
        lemmatized_tokens = [self.lemmatizer.lemmatize(token, self.get_wordnet_pos(token)) for token in tokens]
        return lemmatized_tokens

    def extract_time(self, tokens):
        """Extract time information from tokens."""
        time_units = {"minute": "minutes", "hour": "hours", "second": "seconds"}
        time_value = 0
        time_unit = "seconds"
        for i, token in enumerate(tokens):
            if token.isdigit():
                time_value = int(token)
                if i + 1 < len(tokens) and tokens[i + 1] in time_units.values():
                    time_unit = tokens[i + 1]
                break
        return time_value, time_unit

    def command_matches(self, command_tokens, command_set):
        """Check if command tokens match any of the known commands using synonym matching."""
        for token in command_tokens:
            for known_command in command_set:
                if token in known_command:
                    return True
        return False

    def process_command(self, command, commands):
        """Process the input command."""
        command_tokens = self.preprocess_command(command)
        
        # Matching command tokens with known commands
        if self.command_matches(command_tokens, commands):
            return "Known command detected!"
        else:
            return "Unknown command. Let me try searching online!"

# Pseudo Test Case Statements
def test_preprocess_command():
    processor = CommandProcessor()
    command = "Set a reminder for 5 minutes"
    expected_tokens = ["set", "a", "reminder", "for", "5", "minute"]
    assert processor.preprocess_command(command) == expected_tokens, "Tokenization and lemmatization failed"

def test_extract_time():
    processor = CommandProcessor()
    tokens = ["set", "a", "reminder", "for", "5", "minutes"]
    expected_time_value = 5
    expected_time_unit = "minutes"
    time_value, time_unit = processor.extract_time(tokens)
    assert time_value == expected_time_value, "Time value extraction failed"
    assert time_unit == expected_time_unit, "Time unit extraction failed"

def test_command_matches():
    processor = CommandProcessor()
    command_tokens = ["set", "reminder"]
    command_set = {"set reminder", "set timer", "start stopwatch"}
    assert processor.command_matches(command_tokens, command_set), "Command matching failed"

def test_process_command_known():
    processor = CommandProcessor()
    command = "Set a reminder for 5 minutes"
    command_set = {"set reminder", "set timer", "start stopwatch"}
    result = processor.process_command(command, command_set)
    assert result == "Known command detected!", "Known command processing failed"

def test_process_command_unknown():
    processor = CommandProcessor()
    command = "Play some music"
    command_set = {"set reminder", "set timer", "start stopwatch"}
    result = processor.process_command(command, command_set)
    assert result == "Unknown command. Let me try searching online!", "Unknown command processing failed"

# Run the test cases
test_preprocess_command()
test_extract_time()
test_command_matches()
test_process_command_known()
test_process_command_unknown()

print("All tests passed!")