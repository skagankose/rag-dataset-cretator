"""HTML cleaning and conversion to Markdown."""

import re
from typing import Dict, List, Set

from bs4 import BeautifulSoup, NavigableString, Tag
import markdown

from ..core.errors import CleaningError
from ..core.logging import get_logger
from ..utils.text import clean_whitespace, create_heading_path

logger = get_logger("ingest.clean")


class WikipediaHTMLCleaner:
    """Cleans and converts Wikipedia HTML to structured Markdown."""
    
    def __init__(self, strip_sections: bool = True):
        self.strip_sections = strip_sections
        self.sections_to_strip = {
            "see also",
            "references",
            "external links", 
            "further reading",
            "bibliography",
            "notes",
            "citations",
            "sources",
            "footnotes",
        }
    
    def clean_html(self, html_content: str, title: str) -> Dict[str, str]:
        """Clean HTML content and convert to Markdown.
        
        Returns:
            Dict with keys: content, sections, heading_paths
        """
        logger.info(f"Cleaning HTML content for: {title}")
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract main content
            content_parts = []
            sections = []
            heading_paths = []
            current_headings = []
            
            # Process the content
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'div']):
                if element.name.startswith('h'):
                    # Handle headings
                    level = int(element.name[1])
                    heading_text = self._extract_text(element).strip()
                    
                    if not heading_text:
                        continue
                    
                    # Skip sections we want to strip
                    if self.strip_sections and heading_text.lower() in self.sections_to_strip:
                        # Remove this heading and all content until next same-level heading
                        self._remove_section(element, level)
                        continue
                    
                    # Update heading hierarchy
                    if level <= len(current_headings):
                        current_headings = current_headings[:level-1]
                    
                    while len(current_headings) < level - 1:
                        current_headings.append("")
                    
                    if level <= len(current_headings) + 1:
                        if level == len(current_headings) + 1:
                            current_headings.append(heading_text)
                        else:
                            current_headings[level-1] = heading_text
                    
                    # Create markdown heading
                    markdown_heading = f"{'#' * level} {heading_text}\n\n"
                    content_parts.append(markdown_heading)
                    
                    # Track sections
                    sections.append({
                        'level': level,
                        'title': heading_text,
                        'heading_path': create_heading_path(current_headings[:level]),
                        'start_pos': len(''.join(content_parts)) - len(markdown_heading)
                    })
                    
                elif element.name in ['p', 'div']:
                    # Handle paragraphs
                    text = self._extract_text(element).strip()
                    if text:
                        content_parts.append(f"{text}\n\n")
                        
                elif element.name in ['ul', 'ol']:
                    # Handle lists
                    list_items = []
                    for li in element.find_all('li', recursive=False):
                        item_text = self._extract_text(li).strip()
                        if item_text:
                            prefix = "- " if element.name == 'ul' else "1. "
                            list_items.append(f"{prefix}{item_text}")
                    
                    if list_items:
                        content_parts.append('\n'.join(list_items) + '\n\n')
            
            # Combine content
            full_content = ''.join(content_parts)
            
            # Clean up excessive whitespace
            full_content = re.sub(r'\n{3,}', '\n\n', full_content)
            full_content = full_content.strip()
            
            result = {
                'content': full_content,
                'sections': sections,
                'title': title,
                'word_count': len(full_content.split()),
                'char_count': len(full_content),
            }
            
            logger.info(f"Cleaned content: {result['word_count']} words, {result['char_count']} chars")
            return result
            
        except Exception as e:
            raise CleaningError(f"Failed to clean HTML content: {e}") from e
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements."""
        # Remove script and style elements
        for element in soup.find_all(['script', 'style', 'noscript']):
            element.decompose()
        
        # Remove navigation elements
        for element in soup.find_all(class_=['navbox', 'navbar', 'navigation']):
            element.decompose()
        
        # Remove infoboxes (often contain structured data, not prose)
        for element in soup.find_all(class_=['infobox']):
            element.decompose()
        
        # Remove citation elements
        for element in soup.find_all(class_=['reference', 'citation']):
            element.decompose()
        
        # Remove edit links
        for element in soup.find_all(class_=['mw-editsection']):
            element.decompose()
        
        # Remove table of contents
        for element in soup.find_all(id=['toc']):
            element.decompose()
        
        # Remove most tables (keep simple ones)
        for table in soup.find_all('table'):
            if not self._is_simple_table(table):
                table.decompose()
    
    def _is_simple_table(self, table: Tag) -> bool:
        """Check if table is simple enough to keep."""
        rows = table.find_all('tr')
        if len(rows) > 10:  # Too many rows
            return False
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) > 5:  # Too many columns
                return False
        
        return True
    
    def _extract_text(self, element: Tag) -> str:
        """Extract clean text from an element."""
        # Get all text, preserving some spacing
        text = element.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = clean_whitespace(text)
        
        # Remove citation markers like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove other bracketed content that looks like citations
        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[when\?\]', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _remove_section(self, heading_element: Tag, level: int) -> None:
        """Remove a section and all its content until the next same-level heading."""
        current = heading_element.next_sibling
        
        while current:
            next_sibling = current.next_sibling
            
            if current.name and current.name.startswith('h'):
                current_level = int(current.name[1])
                if current_level <= level:
                    break  # Found next section at same or higher level
            
            if hasattr(current, 'decompose'):
                current.decompose()
            
            current = next_sibling
        
        # Remove the heading itself
        heading_element.decompose()


def clean_wikipedia_html(html_content: str, title: str, strip_sections: bool = True) -> Dict[str, str]:
    """Convenience function to clean Wikipedia HTML."""
    cleaner = WikipediaHTMLCleaner(strip_sections=strip_sections)
    return cleaner.clean_html(html_content, title) 