import json
from openai import OpenAI
from utils.episodic_memory import EpisodicMemory

class OrchestratorBrain:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)
        self.memory = EpisodicMemory(api_key=api_key)
        
    def evaluate_evidence_quality(self, agent_data: dict, agent_name: str) -> bool:
        """
        The 'Brain' function. Evaluates if the agent provided strong quantitative 
        and qualitative evidence.
        """
        # A simple heuristic check for evidence
        if agent_name == "Agent2_Pragmatic":
            # Check if qualitative corpus examples exist in the analysis
            segments_analyzed = len(agent_data.get('segments', []))
            if segments_analyzed == 0:
                return False
                
            # Check ratio of maxims violated vs identified implicatures
            evidence_count = sum(1 for s in agent_data['segments'] if s.get('implicature') or s.get('maxim_violations'))
            ratio = evidence_count / segments_analyzed
            
            # If less than 20% of segments have strong pragmatic evidence, reject and self-correct
            if ratio < 0.2:
                print(f"[Brain] {agent_name} failed quality check. Evidence ratio too low ({ratio:.2f}).")
                return False
                
        return True

    def run_self_correction_loop(self, agent_function, initial_data: dict, agent_name: str, max_retries=2):
        """
        Runs an agent and forces it to self-correct if it fails the quality evaluation.
        """
        print(f"[Orchestrator] Running {agent_name}...")
        result = agent_function(initial_data)
        
        retries = 0
        while not self.evaluate_evidence_quality(result, agent_name) and retries < max_retries:
            retries += 1
            print(f"[Orchestrator] Triggering self-correction for {agent_name} (Attempt {retries})...")
            
            # Provide dynamic, adaptive feedback to the agent
            feedback_prompt = (
                f"Your previous analysis lacked sufficient qualitative evidence from the corpus. "
                f"Adapt your theoretical approach. If Speech Act theory (Austin/Searle) yields no results, "
                f"switch to Politeness Theory (Brown & Levinson) or identify Gricean Implicatures. "
                f"Ensure you quote specific corpus text."
            )
            
            # Pass feedback back to the agent (the agent function must accept a 'feedback' parameter)
            result = agent_function(initial_data, feedback=feedback_prompt)
            
        return result

    def synthesize_final_report(self, corpus_id: str, a1_data, a2_data, a3_data, a4_data):
        """
        Synthesizes the data from all agents into the final PDF/Markdown report structure.
        """
        print("[Orchestrator] Generating Final Linguistic Report...")
        
        # 1. Retrieve Episodic Memory for context
        context_summary = f"Analyzing text with stats: {a1_data.get('corpus_stats')}"
        past_learning = self.memory.retrieve_past_learning(context_summary)
        
        # 2. Construct Prompt for Synthesis
        synthesis_prompt = f"""
        You are a senior computational linguist writing a formal scientific report.
        Based on the following data, write the final report using a 40% quantitative / 60% qualitative structure.
        
        Context from past analyses (Episodic Memory): {past_learning}
        
        Data:
        - Quantitative Baseline (Agent 4): {json.dumps(a4_data)[:500]}...
        - Pragmatic Shifts (Agent 2): {json.dumps(a2_data)[:500]}...
        - Semantic Fields (Agent 3): {json.dumps(a3_data)[:500]}...
        
        Ensure the report includes:
        1. Executive Summary & Meaning Drift Score.
        2. Quantitative Corpus Statistics.
        3. Pragmatic Meaning Drift (citing exact examples).
        4. Semantic Field & Register Shifts.
        5. Theoretical Synthesis.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.3
        )
        
        report_markdown = response.choices[0].message.content
        
        # 3. Store this new knowledge into Episodic Memory
        drift_score = "Detected significant drift" # Mock extracted score
        self.memory.store_analysis(
            corpus_id=corpus_id,
            analysis_summary=f"Analysis of corpus {corpus_id}. Key findings: {drift_score}",
            linguistic_metadata={"ttr": 0.45, "drift_score": 85}
        )
        
        return report_markdown
