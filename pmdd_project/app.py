import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from agents.agent1_preprocessor import run_agent1
from agents.agent2_pragmatic import run_agent2
from agents.agent3_semantic import run_agent3
from agents.agent4_statistics import run_agent4
from agents.agent5_orchestrator import OrchestratorBrain

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/analyze")
async def analyze_corpus(file: UploadFile = File(...), keywords: str = Form(...)):
    try:
        # Save uploaded file temporarily
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        target_keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        orchestrator = OrchestratorBrain()

        # Agent 1
        a1_data = run_agent1(file_location)
        if "error" in a1_data:
            os.remove(file_location)
            return JSONResponse(status_code=400, content={"error": a1_data["error"]})

        # Agent 2
        a2_data = orchestrator.run_self_correction_loop(
            agent_function=run_agent2,
            initial_data=a1_data,
            agent_name="Agent2_Pragmatic",
            max_retries=1
        )

        # Agent 3
        a3_data = run_agent3(a2_data, target_keywords=target_keywords)

        # Agent 4
        a4_data = run_agent4(a3_data, target_keywords=target_keywords)

        # Agent 5
        final_report = orchestrator.synthesize_final_report(
            corpus_id=file.filename,
            a1_data=a1_data,
            a2_data=a2_data,
            a3_data=a3_data,
            a4_data=a4_data['statistical_analysis']
        )
        
        # Clean up temp file
        if os.path.exists(file_location):
            os.remove(file_location)

        return {
            "status": "success",
            "report": final_report,
            "stats": a4_data['statistical_analysis'],
            "raw_data": a4_data['segments']
        }

    except Exception as e:
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    print("Launching FastAPI Server on http://127.0.0.1:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
