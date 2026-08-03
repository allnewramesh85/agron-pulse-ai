# main.py
import os
import shutil
import json
import asyncio
import subprocess
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Core modular frameworks mapping state

import pipeline
from config import CommonConfig
from nodes import SpecializedAgents
from storage import CacheStore, VectorKnowledgeEngine

cache = CacheStore()
db_engine = VectorKnowledgeEngine()
agents_layer = SpecializedAgents(db_engine)
graph_pipeline = pipeline.MultiAgentBuilder.build_graph(agents_layer)

streamlit_process = None
STREAMLIT_URL = "http://127.0.0.1:8501"


async def remove_processed_media(paths_list: list, delay_seconds: int = 5):
    await asyncio.sleep(delay_seconds)
    for path in paths_list:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global streamlit_process
    os.makedirs("upload_samples", exist_ok=True)
    os.makedirs("optimized_samples", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Pree-seed vectory library bounds with regional data configuration
    # 🚀 Seeding unique, region-specific logs spanning global multi-continent geofences
    regional_docs = [
        "Tomato Early Blight (Alternaria solani) triggers target spots with yellow halos. Heavily driven by humidity over 80%. Protect crops using standard Indian sub-continent Copper Oxychloride mixtures.",
        "Tomato Early Blight (Alternaria solani) triggers concentric dark bands. Use standard systemic broad-spectrum synthetic protectants approved by the EPA.",
        "Vineyard Downy Mildew (Plasmopara viticola) active. Apply eco-compliant copper threshold compounds strictly under European safety guidelines."
    ]
    regional_metadata = [
        {"region": "ASIA_APAC_SOUTH"},
        {"region": "NORTH_AMERICA_AMER_NORTH"},
        {"region": "EUROPE_EURO_WEST"}
    ]


    db_engine.seed_initial_knowledge(regional_docs, regional_metadata)

    #Launch Streamlit purely headlessly. FastAPI endpoint stays independent of base URLs.
    print("[SYSTEM] Deploying Streamlit on internal isolated port 8501...")
    streamlit_process = subprocess.Popen([
        "uv", "run", "streamlit", "run", "app_ui.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ],
    stdout=sys.stdout,
    stderr=sys.stderr) #Redirect standard output and error

    yield

    if streamlit_process:
        print("[SYSTEM] Killing internal Streamlit deployment...")
        streamlit_process.terminate()
        streamlit_process.wait()


app = FastAPI(title="AgronPulse AI Monolith Engine", version="2.2.0", lifespan=lifespan)

# Enforce open global CORS rules to allow cross-port bridging across the unified server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root_redirect():
    # Redirects root traffic directly to the active operational UI container port
    return RedirectResponse(url="http://localhost:8501")


# ==========================================
# 🎯 FIXED AND UNBLOCKED BACKEND API ROUTE
# ==========================================
@app.post("/api/v1/diagnose")
async def async_diagnose_endpoint(
    background_tasks: BackgroundTasks,
    user_query: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    thread_id: str = Form("anonymous_field_run"),
    file: UploadFile = File(...)
):
    print(f"📡 [API Core] Ingesting request for thread: {thread_id}")
    local_file_path = f"upload_samples/{file.filename}"
    with open(local_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_name = os.path.basename(local_file_path)
    name, _ = os.path.splitext(base_name)
    optimized_file_path = f"optimized_samples/{name}_optimized.jpg"
    cleanup_targets = [local_file_path, optimized_file_path]

    try:
        cache_key = cache.generate_key(local_file_path, user_query)
        cached_response = cache.get(cache_key)
        if cached_response:
            print("🚀 [Fast-Cache Hit] Intercepted execution path.")
            background_tasks.add_task(remove_processed_media, cleanup_targets)
            return json.loads(cached_response)

        initial_state = {
            "image_path": "",
            "raw_media_path": local_file_path,
            "user_query": user_query,
            "latitude": latitude,
            "longitude": longitude,
            "visual_features": "",
            "is_valid_plant": False,
            "rag_context": "",
            "weather_data": {},
            "pesticide_restrictions": [],
            "final_diagnostic": {}
        }

        final_state = await graph_pipeline.ainvoke(initial_state, config={"configurable": {"thread_id": thread_id}})
        result_payload = final_state.get("final_diagnostic", {})

        if final_state.get("is_valid_plant", False):
            cache.set(cache_key, json.dumps(result_payload))

        background_tasks.add_task(remove_processed_media, cleanup_targets)
        return result_payload
    except Exception as e:
        background_tasks.add_task(remove_processed_media, cleanup_targets)
        raise HTTPException(status_code=500, detail=str(e))