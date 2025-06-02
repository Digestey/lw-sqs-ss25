"""
Module QuizInfo

Contains the model for the Quiz data.
"""
class QuizInfo:
    """Object containing information about the pokemon the user is to be quizzed about.
    """
    def __init__(self, name, pokemon_id, height, weight, stats, types, entry):
        self.name = name
        self.pokemon_id = pokemon_id
        self.height = height
        self.weight = weight
        self.stats = stats
        self.types = types
        self.entry = entry
