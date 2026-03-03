import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    
    return chunks

def generate_doc_id(text: str, source: str) -> str:
    """Generate a unique document ID"""
    if not text or not source:
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()
    
    content = f"{source}:{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()

def load_kb_documents(kb_path: Path) -> List[Dict[str, Any]]:
    """Load all knowledge base documents from directory"""
    documents = []
    
    if not kb_path.exists():
        print(f"Warning: KB path {kb_path} does not exist. Creating empty directory.")
        kb_path.mkdir(parents=True, exist_ok=True)
        return documents
    
    txt_files = list(kb_path.glob("*.txt"))
    
    if not txt_files:
        print(f"Warning: No .txt files found in {kb_path}")
        return documents
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"Warning: {file_path.name} is empty")
                continue
            
            content = clean_text(content)
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                # Determine category from filename
                category = 'general'
                filename_lower = file_path.stem.lower()
                if 'api' in filename_lower:
                    category = 'technical'
                elif any(word in filename_lower for word in ['bill', 'pay', 'price', 'cost']):
                    category = 'billing'
                elif any(word in filename_lower for word in ['login', 'password', 'account']):
                    category = 'account'
                elif any(word in filename_lower for word in ['sla', 'service', 'support']):
                    category = 'support'
                
                # Create document with proper metadata structure
                doc = {
                    "id": generate_doc_id(chunk, file_path.stem),
                    "title": file_path.stem.replace('_', ' ').title(),
                    "content": chunk,
                    "source": file_path.name,
                    "chunk_index": i,
                    "metadata": {
                        "category": category,
                        "filename": file_path.name,
                        "last_updated": datetime.now().isoformat(),
                        "chunk": i + 1,
                        "total_chunks": len(chunks)
                    }
                }
                documents.append(doc)
                
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            continue
    
    print(f"Loaded {len(documents)} document chunks from {len(txt_files)} files")
    return documents

def format_context(documents: List[Dict[str, Any]], max_chars: int = 1000) -> str:
    """Format retrieved documents into a context string"""
    if not documents:
        return "No relevant information found in knowledge base."
    
    context_parts = []
    total_chars = 0
    
    for doc in documents:
        # Safely access metadata
        metadata = doc.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        category = metadata.get("category", "general")
        title = doc.get("title", "Unknown")
        
        header = f"[Source: {title} (Category: {category})]"
        content = doc.get("content", "")
        
        if total_chars + len(header) + len(content) + 10 > max_chars:
            remaining = max_chars - total_chars - len(header) - 10
            if remaining > 50:
                content = content[:remaining] + "..."
                part = f"{header}\n{content}\n"
                context_parts.append(part)
            break
        else:
            part = f"{header}\n{content}\n---\n"
            context_parts.append(part)
            total_chars += len(part)
    
    return "\n".join(context_parts)