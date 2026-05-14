import json
import os
from openai import OpenAI

def run_agent3(agent2_data: dict, target_keywords: list, feedback: str = None) -> dict:
    """
    Agent 3: Semantic Field & Register Detector
    Maps vocabulary drift across semantic fields and identifies register shifts.
    Uses OpenAI to cluster words into semantic fields based on context.
    """
    print("[Agent 3] Starting Semantic Field & Register Analysis...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    segments = agent2_data.get('segments', [])
    
    system_prompt = """
    You are an expert in Lexical Semantics and Register Analysis.
    Given the text segment, identify:
    1. Semantic Field: Classify the primary semantic domain (e.g., 'CONFLICT', 'ECONOMY', 'COMMUNITY', 'POWER').
    2. Register: Classify the tone/register (Formal, Informal, Technical, Colloquial, Bureaucratic).
    3. Keyword Context: If any of the target keywords appear, explain their exact contextual meaning in this sentence.
    
    Return ONLY valid JSON:
    {"semantic_field": "...", "register": "...", "keyword_context": {"keyword": "contextual meaning"}}
    """

    if feedback:
        print("[Agent 3] Applying self-correction feedback from Orchestrator...")
        system_prompt += f"\nCRITICAL INSTRUCTION FROM ORCHESTRATOR: {feedback}"

    enriched_segments = []
    
    # Process up to 10 segments for demonstration to avoid API timeouts
    process_limit = min(10, len(segments))
    keywords_str = ", ".join(target_keywords)
    
    for i in range(process_limit):
        seg = segments[i]
        
        # Only query LLM if the segment has substance or contains keywords (optimization)
        contains_keyword = any(kw.lower() in seg['text'].lower() for kw in target_keywords)
        
        if contains_keyword or i % 3 == 0:  # Sample every 3rd sentence if no keywords
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt + f"\nTarget Keywords: {keywords_str}"},
                        {"role": "user", "content": f"Analyze this segment: '{seg['text']}'"}
                    ],
                    temperature=0.2,
                    response_format={ "type": "json_object" }
                )
                
                analysis = json.loads(response.choices[0].message.content)
                enriched_segments.append({**seg, **analysis})
                
            except Exception as e:
                print(f"[Agent 3] Error processing segment {seg['id']}: {e}")
                enriched_segments.append(seg)
        else:
            enriched_segments.append(seg)
            
    return {
        'corpus_stats': agent2_data.get('corpus_stats'),
        'segments': enriched_segments
    }
