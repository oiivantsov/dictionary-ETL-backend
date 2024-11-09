from pydantic import BaseModel
from typing import Optional

class WordData(BaseModel):
    date_added: Optional[str] = None
    date_repeated: Optional[str] = None
    level: Optional[int] = None
    word: str
    translation: Optional[str] = None
    category: Optional[str] = None
    category2: Optional[str] = None
    source: Optional[str] = None
    popularity: Optional[int] = None
    repeat_again: Optional[int] = None
    comment: Optional[str] = None
    example: Optional[str] = None
    synonyms: Optional[str] = None
    word_formation: Optional[str] = None
    frequency: Optional[int] = None
