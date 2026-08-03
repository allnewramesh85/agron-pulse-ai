import hashlib
import os.path
from webbrowser import Chrome

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core import retrievers

from config import CommonConfig

from typing import List, Dict, Optional


class CacheStore:
    """
    Cache for identical visual and textual request signatures
    """
    def __init__(self) -> None:
        self._cache: Dict[str, str] = {}

    def _calculate_md5(self, path:str)-> str:
        if not os.path.exists(path):
            return "null_file_hash"
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def generate_kv(self, path:str, query: str)-> str:
        """
        Generates a key value pair
        :param path: Image path
        :param query: User query
        :return: cache:key_hash:query:hash
        """
        img_hash = self._calculate_md5(path)
        query_hash = hashlib.md5(query.strip().lower().encode('utf-8')).hexdigest()
        return f"cache:{img_hash}:{query_hash}"
    def get(self, key:str) -> Optional[str]:
        return self._cache.get(key)

    def set(self, key:str, value:str) -> None:
        self._cache[key] = value


class VectorKnowledgeEngine:
    """
    Manages semantic similarity searches across localized agriculture datasets
    """
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=CommonConfig.EMBEDDING_MODEL)
        self.vector_store = Chroma(
            collection_name= CommonConfig.COLLECTION_NAME,
            embedding_function= self.embeddings,
            persist_directory= CommonConfig.VECTOR_DB_DIR
        )

    def seed_initial_knowledge(self, documents: List[str], metadata: List[Dict[str, str]]) -> None:
        """
        Seeds the initial knowledge database
        :param metadata:
        :param documents:
        :return: None
        """
        if len(self.vector_store.get()['ids']) == 0:
            print(f"[Storage] DB is empty. Populating hyper-local regional disease data...")
            self.vector_store.add_texts(texts=documents, metadata=metadata)

    def query_similarity_with_geofence(self, search_text: str, region_tag: str, top_k: int = 2) -> str:
        """
        GEOFENCED FILTER: Forces ChromaDB to query exclusively inside
        the metadata partition matching the field for given region.
        :param region_tag:
        :param search_text:
        :param top_k:
        :return:
        """
        query_embedding = self.embeddings.embed_query(search_text)
        results = self.vector_store._collection.query(
            query_embeddings =[query_embedding],
            n_results=top_k,
            where={"region_tag": region_tag}
        )

        # metadata_filter = {"region": region_tag}
        # docs = self.vector_store.similarity_search(search_text,
        #                                            k= top_k,
        #                                            filters=metadata_filter)
        # if docs:
        #     return "\n".join([f"- {doc.page_content}" for doc in docs])
        if results and "documents" in results and results["documents"]:
            matched_docs = results["documents"][0]
            if matched_docs:
                return "\n".join([f"- [Database Segment: {region_tag}] {doc}" for doc in matched_docs])
        return "No explicit regional overrides found in the local agronomy library"
