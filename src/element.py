from dataclasses import dataclass, field

@dataclass
class Element:
    tag: str
    attributes: str
    parent: object
    children: list = field(default_factory=list)
    
    def __repr__(self):
        return "<" + self.tag + ">"