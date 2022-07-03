class StarboardRepresentation:

    def __init__(self, _id, suggestions, spotlight, required_stars):
        self.id = _id
        self.suggestions = suggestions
        self.spotlight = spotlight
        self.required_stars = required_stars


    def __str__(self):
        return f"{self.id}  | <#{self.suggestions}>  |  <#{self.spotlight}>"