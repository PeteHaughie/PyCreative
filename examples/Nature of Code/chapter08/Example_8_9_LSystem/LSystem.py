"""
L-system class for Example 8-9: L-System
"""

class LSystem:
    def __init__(self, axiom: str, rules: dict[str, str]):
        self.sentence = axiom  # The sentence (a String)
        self.ruleset = rules  # The ruleset (a HashMap of Rule)

    # Generate the next generation
    def generate(self):
        # An empty string that we will fill
        nextgen = ""
        # For every character in the sentence
        for c in self.sentence:
            # Replace it with itself unless it matches one of our rules
            nextgen += self.ruleset.get(c, c)
        # Replace sentence
        self.sentence = nextgen
