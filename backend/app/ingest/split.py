"""Text splitting strategies for chunking content."""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from ..core.errors import SplittingError
from ..core.logging import get_logger
from ..utils.ids import generate_chunk_id
from ..utils.text import count_tokens_estimate, create_heading_path, extract_preview

logger = get_logger("ingest.split")


class ChunkInfo:
    """Information about a text chunk."""
    
    def __init__(
        self,
        id: str,
        content: str,
        start_char: int,
        end_char: int,
        section: str = "",
        heading_path: str = "Lead",
        token_start: int = 0,
        token_end: int = 0,
    ):
        self.id = id
        self.content = content
        self.start_char = start_char
        self.end_char = end_char
        self.section = section
        self.heading_path = heading_path
        self.token_start = token_start
        self.token_end = token_end
        self.char_count = len(content)
        self.token_estimate = count_tokens_estimate(content)
        self.preview = extract_preview(content, 200)


class TextSplitter(ABC):
    """Abstract base class for text splitters."""
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def split_text(self, text: str, sections: List[Dict] = None) -> List[ChunkInfo]:
        """Split text into chunks."""
        pass


class RecursiveTextSplitter(TextSplitter):
    """Recursive text splitter that tries to preserve structure."""
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)
        
        # Separators in order of preference
        self.separators = [
            "\n\n\n",  # Multiple newlines
            "\n\n",    # Paragraph breaks
            "\n",      # Single newlines
            ". ",      # Sentence endings
            "! ",      # Exclamation sentences
            "? ",      # Question sentences
            "; ",      # Semicolons
            ", ",      # Commas
            " ",       # Spaces
            "",        # Characters
        ]
    
    def split_text(self, text: str, sections: List[Dict] = None) -> List[ChunkInfo]:
        """Split text recursively trying to preserve natural boundaries."""
        logger.info(f"Splitting text with recursive strategy: {len(text)} chars")
        
        chunks = []
        sections = sections or []
        
        # Split text into initial segments
        segments = self._split_by_separators(text, self.separators)
        
        # Group segments into chunks
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for segment in segments:
            # Check if adding this segment would exceed chunk size
            potential_chunk = current_chunk + segment
            
            if len(potential_chunk) <= self.chunk_size or not current_chunk:
                # Add segment to current chunk
                current_chunk = potential_chunk
            else:
                # Create chunk from current content
                if current_chunk:
                    chunk = self._create_chunk(
                        chunk_index,
                        current_chunk,
                        current_start,
                        current_start + len(current_chunk),
                        sections
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk with overlap
                overlap_start = max(0, current_start + len(current_chunk) - self.chunk_overlap)
                overlap_text = text[overlap_start:current_start + len(current_chunk)]
                
                current_chunk = overlap_text + segment
                current_start = overlap_start
        
        # Add final chunk
        if current_chunk:
            chunk = self._create_chunk(
                chunk_index,
                current_chunk,
                current_start,
                current_start + len(current_chunk),
                sections
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _split_by_separators(self, text: str, separators: List[str]) -> List[str]:
        """Split text by separators in order of preference."""
        if not separators:
            return [text]
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        if separator == "":
            # Character-level splitting
            return list(text)
        
        # Split by current separator
        splits = text.split(separator)
        
        # If we get good splits, return them
        if len(splits) > 1:
            # Re-add separator except for last split
            result = []
            for i, split in enumerate(splits[:-1]):
                result.append(split + separator)
            if splits[-1]:  # Add last split if not empty
                result.append(splits[-1])
            return result
        
        # If no splits with current separator, try next one
        if remaining_separators:
            return self._split_by_separators(text, remaining_separators)
        
        return [text]
    
    def _create_chunk(
        self,
        index: int,
        content: str,
        start_char: int,
        end_char: int,
        sections: List[Dict]
    ) -> ChunkInfo:
        """Create a chunk with metadata."""
        chunk_id = generate_chunk_id(index)
        
        # Find the section this chunk belongs to
        section = ""
        heading_path = "Lead"
        
        for sec in sections:
            if sec['start_pos'] <= start_char:
                section = sec['title']
                heading_path = sec['heading_path']
            else:
                break
        
        return ChunkInfo(
            id=chunk_id,
            content=content.strip(),
            start_char=start_char,
            end_char=end_char,
            section=section,
            heading_path=heading_path,
        )


class HeaderAwareTextSplitter(TextSplitter):
    """Header-aware text splitter that creates one chunk per section.
    
    Each MediaWiki-style header (== Header ==) or Markdown header (## Header)
    defines a section boundary. Each section becomes exactly one chunk,
    regardless of its size. This ensures semantic coherence and prevents
    mixing content from different sections.
    """
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)
        
        # Regex patterns to match both markdown and MediaWiki headers
        # NOTE: MediaWiki headers are detected anywhere in the line, not only at the start.
        # This is important because cleaned Wikipedia text can have inline headers like:
        # "Lead sentence. == Header == next sentence"
        self.markdown_header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.mediawiki_header_pattern = re.compile(r'(={1,6})\s*(.+?)\s*\1(?=\s|$)')
    
    def split_text(self, text: str, sections: List[Dict] = None) -> List[ChunkInfo]:
        """Split text by header sections only, creating one chunk per section regardless of size."""
        logger.info(f"Splitting text with header-aware strategy: {len(text)} chars")
        
        chunks = []
        metadata_sections = sections or []
        
        # Find all headers and create section boundaries
        # This extracts the actual text sections from content
        text_sections = self._extract_sections(text)
        
        logger.info(f"Found {len(text_sections)} sections for splitting")
        
        chunk_index = 0
        
        for section in text_sections:
            section_chunks = self._split_section(section, chunk_index, metadata_sections)
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        logger.info(f"Created {len(chunks)} chunks from {len(text_sections)} sections")
        return chunks
    
    def _extract_sections(self, text: str) -> List[Dict]:
        """Extract sections based on headers.
        
        Handles all MediaWiki header levels (= to ======).
        """
        sections = []
        
        # Regex pattern to match MediaWiki headers: = Header =, == Header ==, === Header ===, etc.
        # Note: The closing = must be followed by whitespace or end of line, not other text.
        # We deliberately do NOT anchor to start-of-line so inline headers are also detected.
        header_pattern = re.compile(r'(={1,6})\s*(.+?)\s*\1(?=\s|$)')
        
        # Find all headers
        matches = list(header_pattern.finditer(text))
        
        # Handle lead section (content before first header)
        if matches:
            first_header_start = matches[0].start()
            if first_header_start > 0:
                lead_content = text[:first_header_start].strip()
                if lead_content:
                    sections.append({
                        'header': 'Lead',
                        'header_level': 0,
                        'start_pos': 0,
                        'end_pos': first_header_start,
                        'content': lead_content
                    })
        else:
            # No headers found, treat entire content as lead
            if text.strip():
                sections.append({
                    'header': 'Lead',
                    'header_level': 0,
                    'start_pos': 0,
                    'end_pos': len(text),
                    'content': text.strip()
                })
            return sections
        
        # Process each header and its content
        for i, match in enumerate(matches):
            equals = match.group(1)  # The === part
            header_title = match.group(2).strip()  # The title text
            header_level = len(equals)
            
            # Full header with markers
            header_with_markers = f"{equals} {header_title} {equals}"
            
            # Start position of this header
            header_start = match.start()
            header_end = match.end()
            
            # Find content end (either next header or end of text)
            if i + 1 < len(matches):
                content_end = matches[i + 1].start()
            else:
                content_end = len(text)
            
            # Extract section content (header + content)
            section_content = text[header_start:content_end].strip()
            
            # Get content after header (exclude the header line itself)
            content_after_header = text[header_end:content_end].strip()
            
            # Only add sections with actual content (not just empty or whitespace)
            if section_content and content_after_header:
                sections.append({
                    'header': header_with_markers,
                    'header_level': header_level,
                    'start_pos': header_start,
                    'end_pos': content_end,
                    'content': section_content,
                    'header_line_end': header_end
                })
        
        return sections
    
    def _split_section(self, section: Dict, start_chunk_index: int, metadata_sections: List[Dict]) -> List[ChunkInfo]:
        """Split section into chunks - each section becomes exactly one chunk regardless of size.
        
        This ensures that Wikipedia-style sections are not combined, maintaining
        clear semantic boundaries. Each == Header == section becomes its own chunk.
        """
        content = section['content']
        header = section['header']
        section_start = section['start_pos']
        
        logger.debug(f"Processing section '{header}': {len(content)} chars")
        
        # ALWAYS keep each section as a single chunk - never combine sections
        # This is crucial for Wikipedia articles where each section should be independently retrievable
        chunk = self._create_chunk_with_header(
            start_chunk_index,
            content,
            section_start,
            section['end_pos'],
            header,
            metadata_sections
        )
        logger.debug(f"Section '{header}' -> 1 chunk ({len(content)} chars)")
        return [chunk]
    
    def _create_chunk_with_header(
        self,
        index: int,
        content: str,
        start_char: int,
        end_char: int,
        header: str,
        metadata_sections: List[Dict]
    ) -> ChunkInfo:
        """Create a chunk with header information."""
        chunk_id = generate_chunk_id(index)
        
        # Find the section this chunk belongs to from metadata
        section = header
        heading_path = header if header != 'Lead' else 'Lead'
        
        # Try to match with metadata sections for more detailed heading path
        for sec in metadata_sections:
            if sec['start_pos'] <= start_char:
                if 'heading_path' in sec:
                    heading_path = sec['heading_path']
                if 'title' in sec:
                    section = sec['title']
            else:
                break
        
        return ChunkInfo(
            id=chunk_id,
            content=content,
            start_char=start_char,
            end_char=end_char,
            section=section,
            heading_path=heading_path,
        )


def create_text_splitter(strategy: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> TextSplitter:
    """Create a text splitter based on strategy."""
    if strategy == "recursive":
        return RecursiveTextSplitter(chunk_size, chunk_overlap)
    elif strategy == "header_aware":
        return HeaderAwareTextSplitter(chunk_size, chunk_overlap)
    else:
        raise SplittingError(f"Unknown splitting strategy: {strategy}")


def split_content(
    content: str,
    sections: List[Dict],
    strategy: str = "header_aware",
    chunk_size: int = 1200,
    chunk_overlap: int = 200
) -> List[ChunkInfo]:
    """Convenience function to split content."""
    splitter = create_text_splitter(strategy, chunk_size, chunk_overlap)
    return splitter.split_text(content, sections)
