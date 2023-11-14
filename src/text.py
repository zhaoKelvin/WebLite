from dataclasses import dataclass, field

@dataclass
class Text:
    text: str
    parent: object
    children: list = field(default_factory=list)
    is_focused: bool = field(default=False)
    
    def __repr__(self):
        return repr(self.text)