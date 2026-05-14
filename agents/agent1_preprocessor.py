import re

def run_agent1(file_path: str) -> dict:
    """
    Agent 1: Corpus Preprocessor & Segmenter
    Reads a text file, cleans it, and segments it into sentences using regex.
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
    
    # 3. Segment and Tokenize using Regex
    # Split by standard sentence delimiters (. ! ?)
    raw_sentences = re.split(r'(?<=[.!?]) +', text)
    
    segments = []
    total_words = 0
    total_sents = len(raw_sentences)
    
    for i, sent in enumerate(raw_sentences):
        clean_sent = sent.strip()
        if not clean_sent:
            continue
            
        words = re.findall(r'\b\w+\b', clean_sent)
        word_count = len(words)
        total_words += word_count
        
        segments.append({
            'id': i,
            'text': clean_sent,
            'word_count': word_count,
            'position_ratio': round(i / max(1, total_sents), 3)
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
