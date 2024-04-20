
class Persona():
    def __init__(self, data):
        self.tag = data.get('personaTag', None)
        self.enabled = data.get('obj', {'Enabled': False}).get('Enabled', False)
        self.nickname = data.get('nickname', None)
        
    def __repr__(self) -> str:
        return str(vars(self))
    