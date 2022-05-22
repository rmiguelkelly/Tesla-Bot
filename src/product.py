from dataclasses import dataclass

@dataclass 
class Product:

    id: str
    name: str
    price: str
    link: str
    category: str

    def __hash__(self) -> int:
        return self.id.__hash__()
