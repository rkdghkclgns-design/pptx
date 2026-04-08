from typing import Literal, Optional
from pydantic import BaseModel


class SlideData(BaseModel):
    type: Literal[
        "cover",
        "content",
        "twoColumn",
        "threeCards",
        "table",
        "quote",
        "section",
        "closing",
    ]
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    bullets: Optional[list[str]] = None
    notes: Optional[str] = None
    tableHeaders: Optional[list[str]] = None
    tableRows: Optional[list[list[str]]] = None
    imagePrompt: Optional[str] = None
    imageUrl: Optional[str] = None


class PresentationData(BaseModel):
    slides: list[SlideData]
