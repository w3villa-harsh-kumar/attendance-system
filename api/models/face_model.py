from typing import List
from pydantic import BaseModel

class ImageData(BaseModel):
    images: List[str]
    username: str
