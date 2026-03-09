from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Slide(BaseModel):
    slide_number: int
    title: str
    bullets: list[str]
    voiceover: str
    image: Optional[str] = None
    image_prompt: Optional[str] = None

    # Media fields (optional, populated later)
    audio_path: Optional[str] = None
    audio_duration: Optional[float] = None
    image_path: Optional[str] = None


class Lesson(BaseModel):
    title: str
    slides: List[Slide]


# phase 4 storyboard layer
class Scene(BaseModel):
    headline: str = Field(..., max_length=60)
    highlight_word: str = Field(..., max_length=30)
    key_points: List[str] = Field(..., min_items=2, max_items=3)
    icon: str = Field(..., max_length=30)
    animation: str = Field(..., max_length=20)


class Storyboard(BaseModel):
    scenes: List[Scene] = Field(..., min_items=4, max_items=8)
