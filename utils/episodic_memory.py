import os
import json
from openai import OpenAI
# Note: For Vercel production, we will use Pinecone as our serverless vector database
# pip install pinecone-client openai
try:
    from pinecone import Pinecone
except ImportError:
    Pinecone = None

class EpisodicMemory:
    def __init__(self, api_key: str = None, pinecone_key: str = None, index_name: str = "pmdd-memory"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.index_name = index_name
        self.pc = None
        self.index = None
        
        if Pinecone and (pinecone_key or os.getenv("PINECONE_API_KEY")):
            self.pc = Pinecone(api_key=pinecone_key or os.getenv("PINECONE_API_KEY"))
            # Connect to index if it exists
            if self.index_name in [idx.name for idx in self.pc.list_indexes()]:
                self.index = self.pc.Index(self.index_name)

    def get_embedding(self, text: str) -> list:
        """Generate embedding vector using OpenAI's embedding model."""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def store_analysis(self, corpus_id: str, analysis_summary: str, linguistic_metadata: dict):
        """Stores the result of a linguistic analysis in the episodic memory."""
        if not self.index:
            print(f"[Memory Warning] Pinecone not configured. Skipping episodic storage for {corpus_id}")
            return False
            
        vector = self.get_embedding(analysis_summary)
        
        # Store in Pinecone with metadata
        self.index.upsert(
            vectors=[{
                "id": corpus_id, 
                "values": vector, 
                "metadata": {
                    "summary": analysis_summary,
                    "metrics": json.dumps(linguistic_metadata)
                }
            }]
        )
        print(f"[Memory] Successfully stored episodic memory for corpus: {corpus_id}")
        return True

    def retrieve_past_learning(self, current_corpus_context: str, top_k: int = 2) -> str:
        """Retrieves similar past analyses to adapt the current agent approach."""
        if not self.index:
            return "No previous episodic memory accessible."
            
        vector = self.get_embedding(current_corpus_context)
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        
        past_learnings = []
        for match in results.matches:
            if match.score > 0.75: # Only use highly relevant past memories
                past_learnings.append(match.metadata.get("summary", ""))
                
        if past_learnings:
            return "Past Episodic Knowledge: " + " | ".join(past_learnings)
        return "No highly relevant past episodic memory found for this context."
