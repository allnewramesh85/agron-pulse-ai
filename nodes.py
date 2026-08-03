import logging
import os
from pickletools import optimize

import cv2
from PIL import Image
import asyncio
import json
from typing import Dict, Any, Literal

from langchain_community.llms.ollama import Ollama
from tools import AgrochemicalRegistryTool, RealTimeWeatherTool, GeofenceResolutionTool
from config import CommonConfig
from state import AgentState
from storage import VectorKnowledgeEngine
from langchain_ollama import OllamaLLM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgronPulseAgent")

class SpecializedAgents:
    """
    Define isolated processing units across specific specialized agents.
    """
    def __init__(self, db_engine: VectorKnowledgeEngine) -> None:
        self.llm = OllamaLLM(
            model=CommonConfig.LLM_MODEL,
            temperature=CommonConfig.LLM_TEMPERATURE
        )
        self.db_engine = db_engine

    async def media_optimization_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """
        AGENT 0: Intercept raw video or high-resolution images.
         Resize imagery, extract structural focus frames from video streams and downsamples tokens.
        :param state:
        :return:
        """
        logger.info("[Media Optimization Agent]  Processing and optimize raw asset tokens...")
        raw_path = state['raw_media_path']
        optimized_dir = CommonConfig.OPTIMIZED_ASSET_DIR

        os.makedirs(optimized_dir, exist_ok=True)

        base_name = os.path.basename(raw_path)
        name, ext = os.path.splitext(base_name)
        optimized_img_path = os.path.join(optimized_dir, f"{name}_optimized.jpg") #{ext}")

        ext_lower = ext.lower()
        # img: Image.Image | None = None

        # --- VIDEO PROCESSING CHANNEL ---
        if ext_lower in [".mp4", ".avi", ".mov", ".mkv"]:
            logger.info(f"[Media Optimization Agent] Video stream detected. Extracting frames from raw {raw_path}")
            cap = cv2.VideoCapture(raw_path)
            best_frame = None
            # Read sample frame across the timeline to find the sharpest macro focus leaf frame
            count = 0
            max_variance = CommonConfig.CV_MAX_VARIANCE
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or count > 150: #Cap scan range to save CPU cycles
                    break
                if count % 15 == 0: #Sample every 15th frame
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian = cv2.Laplacian(gray, cv2.CV_64F).var() # Blur threshold filter
                    if laplacian > max_variance:
                        max_variance = laplacian
                        best_frame = frame
                count += 1
            cap.release()

            if best_frame is not None:
                #Convert OpenCV array format back to Pillow
                img = Image.fromarray(cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB))
            else:
                raise ValueError("Could not extract good frame structure from video stream")
            # ---IMAGE PROCESSING CHANNEL ---
        else:
            logger.info(f"[Media Optimization Agent] Image file detected. Compressing dimension for {raw_path}")
            img = Image.open(raw_path)


        # Unified downsampling and token reduction
        if img is not None:
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            if img.mode != "RGB":
                img = img.convert('RGB')
        else:
            raise ValueError("[Media Optimization Agent] No image loaded to downsize")

        img.save(optimized_img_path, "JPEG", quality=85)
        logger.info(f"[Media Optimization Agent] Media optimization complete. Token-ready asset written to {optimized_img_path}")
        state["image_path"] = optimized_img_path
        return state


    async def validation_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """
        AGENT - 1: Analyse incoming raw data streams for complaince and image quality
        :param state:
        :return:
        """
        logger.info("[Validation Agent] - Processing leaf tissue imagery analysis...")
        prompt = (
            f"[IMAGE: {state['image_path']}] Act as an agronomy data filter. "
            f"Review user context: '{state['user_query']}'. "
            "Determine if this is an authentic plant leaf, stem, or crop sample. "
            "Reply strictly with your reasoning containing the word 'valid crop' or 'invalid structural data'."
        )

        #Offload synchronous Ollama CPU-bound operation to avoid blocking the main thread execution
        # response = await asyncio.to_thread(self.llm.invoke, prompt)
        response = await self.llm.ainvoke(prompt)
        logger.info(f"[Validation Agent] Received validation results {response}")
        is_valid = any(kw in response.lower() for kw in ["valid crop", "leaf", "crop", "tissue","spot", "blight", "invalid"])
        state['is_valid_plant'] = is_valid
        state['visual_features'] = response
        return state

    def conditional_router(self, state: AgentState) -> Literal["rag_node", "error_node"]:
        """
        Evaluate operational tracking matrics to step-route execution router.
        :param state:
        :return:
        """
        if state['is_valid_plant']:
            logger.info("[Router] - Leaf asset is verified. Sending data matrix to RAG database.")
            return "rag_node"
        else:
            logger.info("[Router] - Bad input trace detected. Routing to error termination state.")
            return "error_node"

    async def error_fallback_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Fallback for execution error handler node
        :param state:
        :return:
        """
        logger.info("[Agent Engine] - Executing error handler workflow...")
        return {"final_diagnostic": {"error": "Image could not be validated as standard crop tissue"}}

    async def rag_verifier_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Dynamically resolves the spatial geofence before query parsing.
        :param state:
        :return:
        """
        logger.info("[RAG Verifier] - Querying vector database for overlapping disease reports...")
        target_region = GeofenceResolutionTool.resolve_region(state['latitude'], state['longitude'])
        logger.info(f"[RAG Verifier] Resolved GPS coordinates to geofence: {target_region}")
        #Run isolated, geofenced similarity query
        context = await asyncio.to_thread(
            self.db_engine.query_similarity_with_geofence,
            state['visual_features'],
            target_region,
            2)
        state['rag_context'] = context
        return state

    async def prescription_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """
        AGENT - 2: Aggregate real-time external tool matrices to craft localized scripts.
        :param state:
        :return:
        """
        logger.info("[Prescription Agent] - Concurrently harvesting tool data matrices...")
        #Concurrently gather I/O tasks
        weather_task = RealTimeWeatherTool.fetch_humidity_risk(state['latitude'], state['longitude'])
        chemical_compliance_task = AgrochemicalRegistryTool.get_permitted_treatments(state['latitude'], state['longitude'])

        weather, restricted_list = await asyncio.gather(weather_task, chemical_compliance_task)
        # prompt = (
        #     f"Visual Observations from vision model:\n{state['visual_features']}\n\n"
        #     f"Regional Database Overrides:\n{state['rag_context']}\n\n"
        #     f"Microclimate Analytics:\n{weather}\n\n"
        #     f"Permitted Agro-chemicals List:\n{restricted_list}\n\n"
        #     "Task: Combine this data into a valid JSON object. Do not include markdown tags like ```json. "
        #     "Structure strictly with these exact keys: 'diagnosis', 'confidence', 'weather_risk_factor', 'actionable_treatments'."
        # )
        prompt = (
            f"Visual Observations from vision model:\n{state['visual_features']}\n\n"
            f"Regional Database Overrides:\n{state['rag_context']}\n\n"
            f"Microclimate Analytics:\n{weather if weather else 'NOT AVAILABLE (Proceed with caution. Assume standard regional climate and flag weather risks as UNKNOWN.)'}\n\n"
            f"Permitted Agro-chemicals List:\n{restricted_list if restricted_list else 'NOT AVAILABLE (Strictly enforce non-chemical treatments, biological controls, or cultural practices only. Do not recommend synthetic chemicals.)'}\n\n"
            "Task: Combine this data into a valid JSON object. Do not include markdown tags like ```json. "
            "Structure strictly with these exact keys: 'diagnosis', 'confidence', 'weather_risk_factor', 'actionable_treatments'.\n\n"
            "Special Handling Instructions:\n"
            "1. If Microclimate Analytics is NOT AVAILABLE, set 'weather_risk_factor' to 'UNKNOWN' and ensure 'actionable_treatments' do not depend on specific upcoming weather windows.\n"
            "2. If Permitted Agro-chemicals List is NOT AVAILABLE, restrict 'actionable_treatments' strictly to physical, mechanical, or organic solutions that do not require chemical regulatory clearance."
        )

        # raw_json_response = await asyncio.to_thread(self.llm.invoke, prompt)
        raw_json_response = await self.llm.ainvoke(prompt)
        logger.info(f"[Prescription Agent] - Raw diagnostic response {raw_json_response}")

        try:
            # Clean string data variants if model leaks wrapper styling elements
            if "```json" in raw_json_response:
                raw_json_response = raw_json_response.replace("```json", "").replace("```", "").strip()

            structured_data = json.loads(raw_json_response)
        except Exception as e:
            logger.error(f"[Prescription Agent] - Failed to prase response {str(e)}")
            structured_data = {
                "diagnosis": "Parsing Error: Gemma did not return raw JSON block structure.",
                "confidence": "Low",
                "weather_risk_factor": weather.get("spore_acceleration_index", "UNKNOWN"),
                "actionable_treatments": restricted_list
            }
        state['final_diagnostic'] =structured_data
        return state
