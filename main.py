import asyncio
import logging
import os, json, shutil
from contextlib import asynccontextmanager
from os.path import exists

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks

import pipeline
from config import CommonConfig
from nodes import SpecializedAgents
from storage import CacheStore, VectorKnowledgeEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgronPulseAgent")
# Setup singleton orchestrator

cache = CacheStore()
db_engine = VectorKnowledgeEngine()
agent_layer = SpecializedAgents(db_engine)
orche_pipeline = pipeline.MultiAgentBuilder.build_graph(agent_layer)


async def remove_processed_media(path_list: list, delay_seconds: int = 5):
    """
    BACKGROUND WORKER: Waits for the response transmission to finish,
    then safely purges the uploaded  asset from disk storage.
    """
    await asyncio.sleep(delay_seconds)
    for file_path in path_list:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"[Pruning Worker] Successfully removed asset: {file_path}")
        except Exception as e:
            logger.error(f"[Pruning Worker] Failed to purge asset {file_path}: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup infrastructure tasks safely using clean Lifespan routing.
    :param app:
    :return:
    """
    os.makedirs("upload_samples", exist_ok=True)
    os.makedirs(CommonConfig.OPTIMIZED_ASSET_DIR, exist_ok=True)
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
    yield
    logger.info("Shutting down core services...")


app = FastAPI(title="DecipherAg Platform", version="1.0.0")


@app.post("/api/v1/diagnose")
async def async_diagnose(background_tasks: BackgroundTasks,
                         user_query: str = Form(...),
                   latitude: float = Form(...),
                   longitude: float = Form(...),
                   thread_id: str = Form("anonymous_field_run"),
                   file: UploadFile = File(...)):
    """
    Highly scalable asynchronized endpoint processing heavy multi-agent analytical graphs.
    Uses proper await metrics to enforce non-blocking server processing loops.
    :param background_tasks:
    :param user_query:
    :param latitude:
    :param longitude:
    :param thread_id:
    :param file:
    :return:
    """
    local_file_path = f"upload_samples/{file.filename}"

    with open(local_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Compile dynamic path markers for background tracking
    base_name = os.path.basename(local_file_path)
    name, _ = os.path.splitext(base_name)
    optimized_file_path = f"{CommonConfig.OPTIMIZED_ASSET_DIR}/{name}_optimized.jpg"
    cleanup_targets = [local_file_path, optimized_file_path]
    try:
        # 1. Quick signature lookup, verify cache
        cache_key = cache.generate_kv(local_file_path, user_query)
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info("[Fast-Cache Hit] Intercepted execution path. Returned stored payload data")
            return json.loads(cached_response)
        # 2. Formulate state dict configuration
        logger.info("[CONTROLLER] Rebuilding dict configuration")
        initial_state = {
            "image_path": local_file_path,
            "raw_media_path": local_file_path,
            "user_query": user_query,
            "latitude": latitude,
            "longitude": longitude,
            "visual_features": [],
            "is_valid_plant": False,
            "rag_contexts": {},
            "weather_data": {},
            "pesticide_restrictions": [],
            "final_diagnosis": {}
        }

        # 3. Secure invocation of the graph state engine using ainvoke
        config = {"configurable": {"thread_id": thread_id}}
        logger.info("[CONTROLLER] Invoking an orchestration pipeline")
        final_state = await orche_pipeline.ainvoke(initial_state, config=config)
        logger.info("[CONTROLLER] Orchestration pipeline response {}".format(final_state))
        payload = final_state["final_diagnostic"]
        # 4. Update the cache if the search is confirmed as valid
        if final_state["is_valid_plant"]:
            logger.info("[CONTROLLER] Caching diagnosis report")
            cache.set(cache_key, json.dumps(payload))
        #Schedule the image removal background worker task right before returning
        background_tasks.add_task(remove_processed_media, cleanup_targets)
        return payload
    except Exception as e:
        logger.error("Pipeline process fauld {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline process Dropped {str(e)}")
