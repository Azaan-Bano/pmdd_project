import re
from collections import Counter
import math

def run_agent4(agent3_data: dict, target_keywords: list) -> dict:
    """
    Agent 4: Corpus Statistician
    Runs purely deterministic algorithms to calculate Type-Token Ratio, 
    collocations, and frequencies. No LLM used.
    """
    print("[Agent 4] Calculating Corpus Statistics...")
    
    segments = agent3_data.get('segments', [])
    corpus_stats = agent3_data.get('corpus_stats', {})
    
    # 1. Build a full word list
    all_words = []
    for seg in segments:
        words = re.findall(r'\b\w+\b', seg['text'].lower())
        all_words.extend(words)
        
    total_words = len(all_words)
    unique_words = len(set(all_words))
    
    # Type-Token Ratio (Lexical Diversity)
    ttr = unique_words / max(1, total_words)
    
    # 2. Global Frequencies
    word_freq = Counter(all_words)
    
    # 3. Collocations for Target Keywords (+/- 5 words window)
    collocations = {kw: Counter() for kw in target_keywords}
    window_size = 5
    
    for i, word in enumerate(all_words):
        for kw in target_keywords:
            if word == kw.lower():
                # Get surrounding words
                start = max(0, i - window_size)
                end = min(len(all_words), i + window_size + 1)
                
                context = all_words[start:i] + all_words[i+1:end]
                # Filter out stopwords (rudimentary list)
                stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                context = [w for w in context if w not in stopwords]
                
                collocations[kw].update(context)
                
    # Format collocations to top 5 per keyword
    top_collocations = {kw: dict(counts.most_common(5)) for kw, counts in collocations.items()}
    
    # Keyword frequencies
    kw_frequencies = {kw: word_freq.get(kw.lower(), 0) for kw in target_keywords}

    # Add statistical data to the output
    stats_output = {
        'type_token_ratio': round(ttr, 4),
        'total_words': total_words,
        'unique_words': unique_words,
        'keyword_frequencies': kw_frequencies,
        'collocations': top_collocations
    }
    
    return {
        'corpus_stats': corpus_stats,
        'statistical_analysis': stats_output,
        'segments': segments
    }
