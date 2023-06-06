import speech_recognition as sr
import re


def replace_spelled_out_numbers(string):
    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
    }
    pattern = re.compile(r"\b(" + "|".join(number_words.keys()) + r")\b")
    return pattern.sub(lambda x: number_words[x.group()], string)


def speech_to_text():
    # create a recognizer instance
    r = sr.Recognizer()

    # create a custom grammar with the word "comma" as an optional separator
    grammar = "place an object at ({x:d} [comma] {y:d})"

    # define a regular expression pattern to match consecutive numbers
    pattern = r"\d+(\.\d+)?\s+\d+(\.\d+)?"
    # define the microphone as a source for audio input
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # transcribe the audio
    try:
        text = r.recognize_google(audio)
        # use the sub() method to replace the matching pattern with the same pattern plus a comma
        output_str = re.sub(pattern, lambda m: m.group().replace(" ", ","), text)
        output_str = output_str.replace("comma", ",")
        output_str = replace_spelled_out_numbers(output_str)
        text = output_str
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        print("Sorry, my speech recognition service is currently down.")


if __name__ == "__main__":
    # speech_to_text()
    a = replace_spelled_out_numbers("I want one apple and two point three oranges")
    print(a)
