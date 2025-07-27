"""Text splitting strategies for chunking content."""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

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


class SentenceTextSplitter(TextSplitter):
    """Sentence-based text splitter using spaCy or NLTK."""
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)
        self.nlp = None
        
        if SPACY_AVAILABLE:
            try:
                # Try to load spaCy model
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, falling back to simple sentence splitting")
    
    def split_text(self, text: str, sections: List[Dict] = None) -> List[ChunkInfo]:
        """Split text by sentences."""
        logger.info(f"Splitting text with sentence strategy: {len(text)} chars")
        
        # Get sentences
        if self.nlp:
            sentences = self._split_with_spacy(text)
        else:
            sentences = self._split_simple(text)
        
        # Group sentences into chunks
        chunks = []
        sections = sections or []
        
        current_chunk_sentences = []
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed chunk size
            if current_length + sentence_length <= self.chunk_size or not current_chunk_sentences:
                current_chunk_sentences.append(sentence)
                current_length += sentence_length
            else:
                # Create chunk from current sentences
                if current_chunk_sentences:
                    chunk_content = " ".join(current_chunk_sentences)
                    start_char = text.find(current_chunk_sentences[0])
                    end_char = start_char + len(chunk_content)
                    
                    chunk = self._create_chunk(
                        chunk_index,
                        chunk_content,
                        start_char,
                        end_char,
                        sections
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences,
                    self.chunk_overlap
                )
                
                current_chunk_sentences = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk_sentences)
        
        # Add final chunk
        if current_chunk_sentences:
            chunk_content = " ".join(current_chunk_sentences)
            start_char = text.find(current_chunk_sentences[0])
            end_char = start_char + len(chunk_content)
            
            chunk = self._create_chunk(
                chunk_index,
                chunk_content,
                start_char,
                end_char,
                sections
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {len(sentences)} sentences")
        return chunks
    
    def _split_with_spacy(self, text: str) -> List[str]:
        """Split text into sentences using spaCy."""
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    def _split_simple(self, text: str) -> List[str]:
        """Simple sentence splitting using regex."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_chars: int) -> List[str]:
        """Get sentences for overlap based on character count."""
        if not sentences or overlap_chars <= 0:
            return []
        
        overlap_sentences = []
        current_overlap = 0
        
        # Take sentences from the end until we reach overlap size
        for sentence in reversed(sentences):
            if current_overlap + len(sentence) <= overlap_chars:
                overlap_sentences.insert(0, sentence)
                current_overlap += len(sentence)
            else:
                break
        
        return overlap_sentences
    
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
    """Header-aware text splitter that splits only by headers, creating one chunk per section regardless of size."""
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)
        
        # Regex patterns to match both markdown and MediaWiki headers
        self.markdown_header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.mediawiki_header_pattern = re.compile(r'^(={1,6})\s*(.+?)\s*\1\s*$', re.MULTILINE)
        
        # Fallback separators for splitting within a section
        self.fallback_separators = [
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
        """Split text by header sections only, creating one chunk per section regardless of size."""
        logger.info(f"Splitting text with header-aware strategy: {len(text)} chars")
        
        chunks = []
        sections = sections or []
        
        # Find all headers and create section boundaries
        text_sections = self._extract_sections(text)
        
        logger.info(f"Found {len(text_sections)} sections for splitting")
        
        chunk_index = 0
        
        for section in text_sections:
            section_chunks = self._split_section(section, chunk_index, sections)
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        logger.info(f"Created {len(chunks)} chunks from {len(text_sections)} sections")
        return chunks
    
    def _extract_sections(self, text: str) -> List[Dict]:
        """Extract sections based on headers."""
        # Split text by MediaWiki headers (== Header ==)
        sections = []
        
        # First, handle the lead section (content before first header)
        parts = text.split('==')
        if parts[0].strip():
            sections.append({
                'header': 'Lead',
                'header_level': 0,
                'start_pos': 0,
                'end_pos': len(parts[0]),
                'content': parts[0].strip()
            })
        
        # Process remaining sections
        current_pos = len(parts[0])
        
        for i in range(1, len(parts)-1, 2):  # Step by 2 to handle header and content pairs
            header_text = parts[i].strip()
            content_text = parts[i+1] if i+1 < len(parts) else ""
            
            # Skip empty headers
            if not header_text:
                continue
                
            # Calculate positions
            header_start = current_pos
            header_with_markers = f"== {header_text} =="
            content_start = header_start + len(header_with_markers)
            content_end = content_start + len(content_text)
            
            # Create section with header included in content
            section_content = f"== {header_text} =={content_text}"
            
            if section_content.strip():  # Only add sections with content
                sections.append({
                    'header': header_with_markers,
                    'header_level': 2,  # MediaWiki headers with == are level 2
                    'start_pos': header_start,
                    'end_pos': content_end,
                    'content': section_content.strip(),
                    'header_line_end': content_start
                })
            
            current_pos = content_end
        
        return sections
    
    def _split_section(self, section: Dict, start_chunk_index: int, metadata_sections: List[Dict]) -> List[ChunkInfo]:
        """Split section into chunks, keeping small sections as single chunks."""
        content = section['content']
        header = section['header']
        section_start = section.get('header_line_end', section['start_pos'])
        
        logger.debug(f"Processing section '{header}': {len(content)} chars")
        
        # If section fits in chunk size, keep it as a single chunk
        if len(content) <= self.chunk_size:
            chunk = self._create_chunk_with_header(
                start_chunk_index,
                content,
                section_start,
                section['end_pos'],
                header,
                metadata_sections
            )
            logger.debug(f"Section '{header}' fits in chunk size, keeping as single chunk")
            return [chunk]
        
        # Section is too large, split it into smaller chunks
        chunks = []
        chunk_index = start_chunk_index
        
        # First chunk should include the header
        current_text = content
        first_chunk_size = self.chunk_size - len(header) - 2  # Account for header and some spacing
        
        # Find a good split point for the first chunk
        split_pos = self._find_section_split_point(current_text, 0, first_chunk_size)
        first_chunk_content = current_text[:split_pos].strip()
        
        if first_chunk_content:
            chunk = self._create_chunk_with_header(
                chunk_index,
                first_chunk_content,
                section_start,
                section_start + split_pos,
                header,
                metadata_sections
            )
            chunks.append(chunk)
            chunk_index += 1
        
        # Process remaining content
        remaining_text = current_text[split_pos:].strip()
        current_pos = split_pos
        
        while remaining_text:
            # Find next split point
            if len(remaining_text) <= self.chunk_size:
                split_pos = len(remaining_text)
            else:
                split_pos = self._find_section_split_point(remaining_text, 0, self.chunk_size)
            
            chunk_content = remaining_text[:split_pos].strip()
            
            if chunk_content:
                abs_start = section_start + current_pos
                abs_end = abs_start + len(chunk_content)
                
                chunk = self._create_chunk_with_header(
                    chunk_index,
                    chunk_content,
                    abs_start,
                    abs_end,
                    header,
                    metadata_sections
                )
                chunks.append(chunk)
                chunk_index += 1
            
            remaining_text = remaining_text[split_pos:].strip()
            current_pos += split_pos
        
        logger.debug(f"Split section '{header}' into {len(chunks)} chunks")
        return chunks
    
    def _find_section_split_point(self, content: str, start_pos: int, max_end: int) -> int:
        """Find the best split point within a section using fallback separators."""
        chunk_text = content[start_pos:max_end]
        
        # Try each separator in order of preference
        for separator in self.fallback_separators:
            if separator == "":
                # Character-level splitting - just use max_end
                return max_end
            
            # Find the last occurrence of the separator in the chunk
            last_sep_pos = chunk_text.rfind(separator)
            if last_sep_pos != -1:
                # Found separator, split after it
                split_pos = start_pos + last_sep_pos + len(separator)
                # Make sure we don't split too early (at least 50% of target chunk size)
                min_split = start_pos + (self.chunk_size // 2)
                if split_pos >= min_split:
                    return split_pos
        
        # If no good separator found, split at max_end
        return max_end
    
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
    
    def _calculate_overlap_start(self, text: str, chunk_start: int, chunk_end: int) -> int:
        """This method is no longer used in the new section-based approach."""
        # This method is kept for compatibility but not used in the new implementation
        return chunk_end
    
    def _find_next_header_split_point(
        self, text: str, start_pos: int, headers: List[re.Match]
    ) -> Tuple[int, str]:
        """This method is no longer used in the new section-based approach."""
        # This method is kept for compatibility but not used in the new implementation
        return len(text), "end of text"
    
    def _find_fallback_split_point(self, text: str, start_pos: int, max_end: int) -> int:
        """This method is no longer used in the new section-based approach."""
        # This method is kept for compatibility but not used in the new implementation
        return max_end


def create_text_splitter(strategy: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> TextSplitter:
    """Create a text splitter based on strategy."""
    if strategy == "recursive":
        return RecursiveTextSplitter(chunk_size, chunk_overlap)
    elif strategy == "sentence":
        return SentenceTextSplitter(chunk_size, chunk_overlap)
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