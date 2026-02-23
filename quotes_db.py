"""
Philosophy Quotes Database Logic
Handles loading, filtering, and retrieving quotes from quotes_db.json
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from quote_model import Quote


class PhilosophyQuotesDB:
    """Manager for philosophy quotes database."""
    
    def __init__(self, db_path: str = "quotes_db.json"):
        """
        Initialize the database.
        
        Args:
            db_path: Path to the JSON database file
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            json.JSONDecodeError: If database file is invalid JSON
        """

        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database file not found: {db_path}\n"
                f"Make sure 'quotes_db.json' is in the same directory as this script."
            )
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to Quote objects
            self.quotes: List[Quote] = [
                Quote.from_dict(q) for q in data.get("quotes", [])
            ]
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in {db_path}: {str(e)}",
                e.doc,
                e.pos
            )
        
        if not self.quotes:
            raise ValueError(f"No quotes found in {db_path}")
        
        print(f"✓ Loaded {len(self.quotes)} philosophy quotes from {db_path}")
        
        # Validation
        errors = self.validate_database()
        if errors:
            print("⚠ Database validation warnings:")
            for error in errors:
                print(f"  - {error}")

    def get_all_quotes(self) -> List[Quote]:
        """Get all quotes from the database."""
        return self.quotes

    def get_quote_by_index(self, index: int) -> Optional[Quote]:
        """Get a single quote by its index (0-based)."""
        if 0 <= index < len(self.quotes):
            return self.quotes[index]
        return None

    def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        """Get a single quote by its ID."""
        for q in self.quotes:
            if q.id == quote_id:
                return q
        return None

    def get_quotes_by_tradition(self, tradition: str) -> List[Quote]:
        """
        Get all quotes from a specific philosophical tradition.
        
        Args:
            tradition: Name of the philosophical tradition (case-insensitive)
            
        Returns:
            List of quotes matching the tradition
        """
        return [
            q for q in self.quotes 
            if q.tradition.lower() == tradition.lower()
        ]

    def get_quotes_by_theme(self, theme: str) -> List[Quote]:
        """
        Get all quotes related to a specific theme.
        
        Args:
            theme: Theme name (case-insensitive)
            
        Returns:
            List of quotes with this theme
        """
        return [
            q for q in self.quotes 
            if theme.lower() in [t.lower() for t in q.themes]
        ]

    def get_quotes_by_author(self, author: str) -> List[Quote]:
        """
        Get all quotes from a specific author.
        
        Args:
            author: Author name (case-insensitive, partial match)
            
        Returns:
            List of quotes by this author
        """
        author_lower = author.lower()
        return [
            q for q in self.quotes 
            if author_lower in q.author.lower()
        ]

    def get_verified_quotes(self, verified: bool = True) -> List[Quote]:
        """Get quotes filtered by verification status."""
        return [q for q in self.quotes if q.verified == verified]

    def find_similar_quotes(
        self, user_quote: str, top_k: int = 3
    ) -> List[Tuple[Quote, int]]:
        """
        Find similar quotes using theme-based scoring.
        
        This method scores quotes based on how many themes from the input
        quote match the themes in database quotes.
        
        Args:
            user_quote: The input quote text to match against
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (Quote, score) sorted by score (descending)
        """
        lowered = user_quote.lower()
        scored: List[Tuple[int, Quote]] = []

        for q in self.quotes:
            score = 0
            
            # Score based on theme matches
            for theme in q.themes:
                if theme.lower() in lowered:
                    score += 1

            if score > 0:
                scored.append((score, q))

        # Sort by score (descending)
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # Return top_k with score
        return [(q, score) for score, q in scored[:top_k]]

    def find_similar_quotes_expanded(
        self, user_quote: str, top_k: int = 3, include_unverified: bool = False
    ) -> List[Tuple[Quote, int]]:
        """
        Enhanced similarity search with verification filtering.
        
        Args:
            user_quote: The input quote text to match against
            top_k: Number of top matches to return
            include_unverified: Whether to include unverified quotes
            
        Returns:
            List of tuples (Quote, score) sorted by score (descending)
        """
        quotes_to_search = self.quotes
        
        if not include_unverified:
            quotes_to_search = [q for q in self.quotes if q.verified]
        
        lowered = user_quote.lower()
        scored: List[Tuple[int, Quote]] = []

        for q in quotes_to_search:
            score = 0
            
            # Score based on theme matches
            for theme in q.themes:
                if theme.lower() in lowered:
                    score += 1

            if score > 0:
                scored.append((score, q))

        # Sort by score (descending)
        scored.sort(reverse=True, key=lambda x: x[0])
        
        return [(q, score) for score, q in scored[:top_k]]

    def get_all_traditions(self) -> List[str]:
        """Get sorted list of all philosophical traditions in database."""
        return sorted(set(q.tradition for q in self.quotes))

    def get_all_themes(self) -> List[str]:
        """Get sorted list of all themes in database."""
        themes = set()
        for q in self.quotes:
            themes.update(q.themes)
        return sorted(themes)

    def get_all_authors(self) -> List[str]:
        """Get sorted list of all authors in database."""
        return sorted(set(q.author for q in self.quotes))

    def search_quotes(self, keyword: str, search_in: str = "text") -> List[Quote]:
        """
        Search quotes by keyword in specified field.
        
        Args:
            keyword: Search term (case-insensitive)
            search_in: Field to search in ("text", "author", "tradition", "themes")
            
        Returns:
            List of matching quotes
        """
        keyword_lower = keyword.lower()
        results = []

        for q in self.quotes:
            if search_in == "text" and keyword_lower in q.text.lower():
                results.append(q)
            elif search_in == "author" and keyword_lower in q.author.lower():
                results.append(q)
            elif search_in == "tradition" and keyword_lower in q.tradition.lower():
                results.append(q)
            elif search_in == "themes":
                if any(keyword_lower in t.lower() for t in q.themes):
                    results.append(q)

        return results

    def get_quotes_as_text_list(self, limit: Optional[int] = None) -> str:
        """
        Get quotes formatted as numbered text list for LLM prompts.
        
        Args:
            limit: Maximum number of quotes to include (None = all)
            
        Returns:
            Formatted string with numbered quotes
        """
        quotes_to_use = self.quotes[:limit] if limit else self.quotes
        return "\n".join(
            [
                f"{i+1}. {q.text} — {q.author}"
                for i, q in enumerate(quotes_to_use)
            ]
        )

    def get_database_stats(self) -> Dict:
        """Get statistics about the database."""
        verified_count = len([q for q in self.quotes if q.verified])
        unverified_count = len(self.quotes) - verified_count
        
        return {
            "total_quotes": len(self.quotes),
            "verified_quotes": verified_count,
            "unverified_quotes": unverified_count,
            "total_traditions": len(self.get_all_traditions()),
            "total_themes": len(self.get_all_themes()),
            "total_authors": len(self.get_all_authors()),
            "traditions": self.get_all_traditions(),
        }

    def validate_database(self) -> List[str]:
        """
        Validate all quotes have required fields and integrity.
        
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        ids = set()

        for i, q in enumerate(self.quotes):
            # Check for duplicate IDs
            if q.id in ids:
                warnings.append(f"Quote {i}: Duplicate ID '{q.id}'")
            ids.add(q.id)

            # Check for unverified quotes
            if not q.verified:
                warnings.append(
                    f"Quote {i}: '{q.text[:50]}...' is unverified "
                    f"({q.attribution_note or 'no note'})"
                )

        return warnings

    def export_as_dict(self) -> Dict:
        """Export entire database as dictionary."""
        return {
            "quotes": [q.to_dict() for q in self.quotes]
        }


def load_quotes_db(db_path: str = "quotes_db.json") -> PhilosophyQuotesDB:
    """
    Load and return the quotes database.
    
    Usage:
        from philosophy_quotes_db import load_quotes_db
        db = load_quotes_db()
        quotes = db.get_all_quotes()
    """

    return PhilosophyQuotesDB(db_path)
