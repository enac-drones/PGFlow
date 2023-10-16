import re
import spacy, ast
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from src.building import Building, RegularPolygon
from src.speech2text import speech_to_text


# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()

stop_words = spacy.lang.en.stop_words.STOP_WORDS
# just to strip potential brackets too
other_stop_words = ["(", ")", "[", "]", "{", "}"]
stop_words.update(other_stop_words)
# print("(" in stop_words)


def PolygonObstacle(sides, position, orientation, radius):
    print(
        f"PolygonObstacle has been called with {sides} sides, position {position}, angle {orientation}, radius {radius}"
    )
    return True


def is_coordinate(token):
    """check if token is of the form x,y where x and y are float-like"""
    if re.match(r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", token.text):
        return True
    return False


# Define a function to check if a token is a synonym of "position"
def is_position(token):
    synonyms = set()
    for syn in wordnet.synsets("position"):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    for syn in wordnet.synsets("place"):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    for syn in wordnet.synsets("set"):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return token.text.lower() in synonyms
    return token in synonyms


def is_rotation(token):
    rotation_keywords = set(
        [
            "rotate",
            "rotation",
            "rotational",
            "rotated",
            "turn",
            "turned",
            "turning",
            "tilt",
            "incline",
            "inclined" "tilted",
            "tilting",
            "angle",
            "angled",
            "angling",
            "orient",
            "orientation",
            "oriented",
            "spin",
        ]
    )

    lemma = lemmatizer.lemmatize(token.text, pos=wordnet.VERB)
    if lemma in rotation_keywords:
        return True
    for syn in wordnet.synsets(token.text):
        for lemma in syn.lemmas():
            lemma_name = lemma.name().lower()
            if lemma_name in rotation_keywords:
                return True
    return False


# Define the function for natural language input
def get_obstacle_from_text(input_text):

    # Parse the input text using spaCy
    # doc = nlp(response.choices[0].text)
    doc1 = nlp(input_text)
    doc = [
        token
        for token in doc1
        if not token.is_stop and token.text.strip() not in stop_words
    ]
    # print(doc)
    # print([token for token in doc])

    # Extract relevant information from the parsed text
    position = (None, None)
    radius = None
    orientation = None
    sides = None
    shape = None
    doc_length = len(doc)
    for index, token in enumerate(doc):
        # print(token, index,doc[index + 1])
        if token.text.lower() in {
            "square",
            "triangle",
            "pentagon",
            "hexagon",
            "heptagon",
            "octagon",
        }:
            shape = token.text.lower()
        elif (
            token.text.lower() == "radius"
            and index < len(doc) - 1
            and doc[index + 1].like_num
        ):
            # print("inside size")
            radius = float(doc[index + 1].text)
        elif (
            is_position(token)
            and index < len(doc) - 1
            and is_coordinate(doc[index + 1])
        ):
            # print("inside position")
            position = tuple(map(float, doc[index + 1].text.split(",")))
        elif is_coordinate(token):
            position = tuple(map(float, token.text.split(",")))
        elif is_rotation(token) and index < len(doc) - 1 and doc[index + 1].like_num:
            orientation = float(doc[index + 1].text)
        elif (
            token.text.lower() == "sides"
            and index < len(doc) - 1
            and doc[index + 1].like_num
        ):
            sides = int(doc[index + 1].text)
        elif (
            token.like_num
            and index > 0
            and index < len(doc) - 1
            and doc[index + 1].text.lower() == "sides"
        ):
            sides = int(token.text)
    # print(position,radius,orientation,sides,shape)
    # Validate input and create the obstacle
    if shape is None and sides is None:
        print("Warning: shape or number of sides not specified, defaulting to square")
        sides = 4
        # return None

    if sides is None:
        shape_dict = {
            "square": 4,
            "triangle": 3,
            "pentagon": 5,
            "hexagon": 6,
            "heptagon": 7,
            "octagon": 8,
        }
        if shape in shape_dict:
            sides = shape_dict[shape]
        else:
            print(f"Warning: invalid shape '{shape}' specified, defaulting to square")
            sides = 4
            # return None

    if position == (None, None):
        print("Warning: position not specified, defaulting to origin")
        position = (0, 0)
        # return None

    if radius is None:
        print("Warning: radius not specified, defaulting to radius of 1")
        radius = 1
        # return None

    if orientation is None:
        print("Warning: orientation not specified, defaulting to no rotation")
        orientation = 0.0

    # print("hi")
    # Use your existing class to create the obstacle
    # obstacle = PolygonObstacle(sides, position, orientation, radius)
    obstacle = RegularPolygon(
        sides=sides, centre=position, rotation=orientation, radius=radius
    )
    building = Building(obstacle.points())
    # print(coords)

    return building


def create_buildings():
    buildings = {}
    i = 0
    while True:
        user_input = input("Specify obstacle using natural language: ")
        # user_input = "Add an heptagon rotated by 45 degrees at a radius of 1 and placed at (2,1)"
        if user_input == "exit":
            break
        elif user_input == "none":
            return list([])
        elif user_input == "json":
            # ask which case they would like from the json case file cases.json
            return "alpha"

        elif user_input == "rm":
            try:
                rm_index = int(input("Specify building to remove: "))
                if rm_index in buildings.keys():
                    buildings.pop(rm_index)
                    print(f"Removed building {rm_index}")
                else:
                    raise ValueError
            except ValueError:
                print(
                    "Error: input must be the the number of the building you wish to remove"
                )

        elif user_input == "buildings":
            print(f"The current buildings are as follows: {buildings}")
        elif user_input == "done":
            print("Building creation complete, running simulation.")
            break
        else:
            if user_input == "voice":
                user_input = speech_to_text()
            obstacle = get_obstacle_from_text(user_input)
            buildings[i] = obstacle
            print(f"this was building {i}")
            i += 1
    # print("should be out of the loop now")
    return [] if len(buildings) == 0 else list(buildings.values())


def create_vehicles():
    """create drone positions and destinations, #FIXME not functional yet"""
    i = 0
    vehicles = {}
    position = (0, 0, 0)
    while True:
        user_input = input(
            f"Specify the position of vehicle {i} in the format (x,y,z=1.2): "
        )
        if user_input == "none":
            return []
        else:
            try:
                # Attempt to convert the user input to a tuple using ast.literal_eval()
                tup = ast.literal_eval(user_input)

                # Check if the converted object is a tuple
                if isinstance(tup, tuple):
                    print("User input is a tuple:", tup)
                    if (
                        isinstance(tup, tuple)
                        and len(tup) == 3
                        and all(type(n) == float or type(n) == int for n in tup)
                    ):
                        position = tup
                    break
                else:
                    print("User input is not a tuple.")

            except ValueError:
                # ast.literal_eval() will raise a ValueError if the input is not a valid Python literal
                print("User input is not a valid Python literal.")

        # elif isinstance(user_input,tuple) and len(user_input)==3 and all(n.isnumeric() for n in user_input):
        #     position = user_input
        #     break
        # else:
        #     print("bro do what I asked plez")
    return position


# print(create_vehicles())
