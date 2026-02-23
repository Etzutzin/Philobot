"""Quote data model with type safety and validation."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Quote:
    """Represents a single philosophy quote with metadata."""
    
    id: str
    text: str
    author: str
    tradition: str
    themes: List[str]
    verified: bool = True
    attribution_note: Optional[str] = None
    source_work: Optional[str] = None
    year: Optional[str] = None

    def __post_init__(self):
        """Validate quote data after initialization."""
        if not self.text or not self.text.strip():
            raise ValueError("Quote text cannot be empty")
        if not self.author or not self.author.strip():
            raise ValueError("Author cannot be empty")
        if not self.themes or len(self.themes) == 0:
            raise ValueError("At least one theme is required")

    def get_attribution_string(self) -> str:
        """Get a formatted attribution string with verification status."""
        base = f"— {self.author}"
        
        if not self.verified:
            base += " [UNVERIFIED]"
        elif self.attribution_note:
            base += f" [{self.attribution_note}]"
        
        if self.source_work:
            base += f" ({self.source_work}"
            if self.year:
                base += f", {self.year}"
            base += ")"
        
        return base

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author,
            "tradition": self.tradition,
            "themes": self.themes,
            "verified": self.verified,
            "attribution_note": self.attribution_note,
            "source_work": self.source_work,
            "year": self.year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        """Create Quote instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            text=data["text"],
            author=data["author"],
            tradition=data["tradition"],
            themes=data["themes"],
            verified=data.get("verified", True),
            attribution_note=data.get("attribution_note"),
            source_work=data.get("source_work"),
            year=data.get("year"),
        )