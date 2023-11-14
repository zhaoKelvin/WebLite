from dataclasses import dataclass, field

@dataclass
class Element:
    tag: str
    attributes: dict
    parent: object
    children: list = field(default_factory=list)
    is_focused: bool = field(default=False)
    
    def __repr__(self):
        return "<" + self.tag + ">"