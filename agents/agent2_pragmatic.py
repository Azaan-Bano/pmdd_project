import json
import os
from openai import OpenAI

# Agent 2 handles Pragmatics: Speech Acts, Gricean Maxims, Implicature, Politeness
def run_agent2(agent1_data: dict, feedback: str = None) -> dict:
    """
    Agent 2: Pragmatic Analyzer
    Loops through segments and classifies pragmatic functions.
    Supports a feedback parameter for self-correction triggered by Agent 5.
    """
    print("[Agent 2] Starting Pragmatic Analysis...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    segments = agent1_data.get('segments', [])
    
    # Base theoretical instructions
    system_prompt = """
    You are a computational pragmatics expert. Analyze the given text segment.
    1. Speech Act (Searle): Assertive, Directive, Commissive, Expressive, Declaration.
    2. Gricean Maxims: Identify violations (Quantity, Quality, Relation, Manner) or "None".
    3. Implicature: "Conventional", "Conversational", or "None".
    4. Politeness Score: 1 (face-threatening) to 5 (highly polite).
    
    Return ONLY valid JSON:
    {"speech_act": "...", "maxim_violations": ["..."], "implicature": "...", "politeness_score": X, "qualitative_evidence": "quote specific words justifying this"}
    """
    
    # If the orchestrator (Agent 5) rejected the last run, we adapt the prompt based on feedback
    if feedback:
        print("[Agent 2] Applying self-correction feedback from Orchestrator...")
        system_prompt += f"\nCRITICAL INSTRUCTION FROM ORCHESTRATOR: {feedback}"

    enriched_segments = []
    
    # For a real large corpus, we would batch these requests. 
    # For this implementation, we will process a small sample (e.g., first 10 segments) to avoid massive API costs,
    # or batch them appropriately. We will process up to 10 for demonstration.
    process_limit = min(10, len(segments))
    
    for i in range(process_limit):
        seg = segments[i]
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this segment: '{seg['text']}'"}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" } # Force JSON output
            )
            
            analysis = json.loads(response.choices[0].message.content)
            # Merge segment data with pragmatic analysis
            enriched_segments.append({**seg, **analysis})
            
        except Exception as e:
            print(f"[Agent 2] Error processing segment {seg['id']}: {e}")
            enriched_segments.append(seg) # Append without analysis on failure
            
    # Return a copy of the corpus stats along with the newly enriched segments
    return {
        'corpus_stats': agent1_data.get('corpus_stats'),
        'segments': enriched_segments
    }
