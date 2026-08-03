from typing import TypedDict, List, Dict, Any
class AgentState(TypedDict) :
    """
    Main state topology mapping immutable variables across multiple agents
    Extensible for IoT Edge attachments like soil moisture indices or canopy area.
    """
    image_path: str
    raw_media_path: str
    user_query: str
    latitude: float
    longitude: float
    altitude: float
    visual_features: List[Dict[str, Any]]
    is_valid_plant: bool
    rag_context: Dict[str, Any]
    weather_data: Dict[str, Any]
    pesticide_restrictions: List[str]
    final_diagnostic: Dict[str, Any]
    
