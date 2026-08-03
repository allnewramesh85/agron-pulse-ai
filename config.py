class CommonConfig:
    """Centralized architecture hyperparameters layer."""
    LLM_MODEL: str = "gemma4:e4b"
    #Route vector calculations to a model that explicitly supports them
    EMBEDDING_MODEL:str = "nomic-embed-text"
    LLM_TEMPERATURE = 0.1

    VECTOR_DB_DIR = "./chroma_db_storage"
    COLLECTION_NAME = "local_crop_knowledge"
    DEFAULT_THREAD_ID = "global_field_zone"
    OPTIMIZED_ASSET_DIR = "optimized_samples"
    CV_MAX_VARIANCE = -1.0