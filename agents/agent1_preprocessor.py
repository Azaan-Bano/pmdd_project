import spacy
import re

# We will load the spaCy model. If it fails, we fall back to a simple sentence splitter.
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("[Agent 1] Downloading en_core_web_sm model...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load('en_core_web_sm')

def run_agent1(file_path: str) -> dict:
    """
    Agent 1: Corpus Preprocessor & Segmenter
    Reads a text file, cleans it, and segments it into sentences.
    """
    print(f"[Agent 1] Processing file: {file_path}")
    
    # 1. Read File
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

    # 2. Clean Text (Remove extra whitespaces, weird symbols)
    text = re.sub(r'\s+', ' ', raw_text).strip()
    
    # 3. Segment and Tokenize
    doc = nlp(text)
    
    segments = []
    total_words = 0
    
    # We will track the relative position of sentences to help Agent 3 with drift over time
    total_sents = len(list(doc.sents))
    
    for i, sent in enumerate(doc.sents):
        clean_sent = sent.text.strip()
        if not clean_sent:
            continue
            
        word_count = len([token for token in sent if not token.is_punct and not token.is_space])
        total_words += word_count
        
        segments.append({
            'id': i,
            'text': clean_sent,
            'word_count': word_count,
            'position_ratio': round(i / max(1, total_sents), 3) # 0.0 (start) to 1.0 (end)
        })

    # 4. Return Structured Data
    return {
        'corpus_stats': {
            'total_sentences': len(segments),
            'total_words': total_words,
            'avg_words_per_sentence': round(total_words / max(1, len(segments)), 2)
        },
        'segments': segments
    }
