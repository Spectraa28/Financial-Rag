# IMPOrts 
# import os
# import re
# import bs4
# from typing import List, Dict
# import chromadb
# from sentence_transformers import SentenceTransformer
# from rank_bm25 import BM25Okapi
# from bs4 import BeautifulSoup

# # Better parsing tools 
# from docling.document_converter import DocumentConverter
# from docling.chunking import HybridChunker
# from transformers import AutoTokenizer

# def enrich_chunk_text(chunk):
#     return f"{chunk['section_title']}:\n{chunk['text']}"

# # INgestion with Docling 
# def ingest_with_docling(file_path: str,company_name: str, doc_type: str, fiscal_year: str) -> list[dict]:
#     """
#     Parses a document using IBM Docling and constructs a list of structured chunks
#     mapped to the downstream vector database schema.
#     """
    
#     print(f"Initializing Docling document converter for {file_path}")
    
#     # Extract the layout aware doc conversion 
#     converter = DocumentConverter()
#     result = converter.convert(file_path)
    
#     tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
#     # INitialize structural chunker 
#     chunker = HybridChunker(tokenizer=tokenizer, max_tokens=256)
    
#     chunks = []
    
#     for i, docling_chunk in enumerate(chunker.chunk(result.document)):
#         text_content = docling_chunk.text.strip()
        
#         if not text_content:
#             continue
        
#         heading_list = docling_chunk.meta.headings if docling_chunk.meta.headings else ["General Document"]
        
#         section_title = heading_list[-1]
        
#         citation_path = ' > '.join(heading_list)
#         citation = f"{company_name} ({fiscal_year}) {doc_type} |  {citation_path}"
        
#         chunk_dict = {
#             "chunk_id": f"{company_name}_{fiscal_year}_chunk_{i}",
#             "company": company_name,
#             "doc_type": doc_type,
#             "fiscal_year": fiscal_year,
#             "section_title": section_title,
#             "citation": citation,
#             "text": text_content
#         }
        
#         chunks.append(chunk_dict)
        
#     print(f" Parsing completed . Generated {len(chunks)} layout aware chunks")

#     return  chunks


# Knowledge Graph
class KnowledgeGraph:
    def __init__(self):
        self._nodes = {}
        self._edges = {}
        self._in_edges = {}
        
    def add_node(self,node_id: str, label:str, node_type:str, **attrs) -> None:
        if node_id  not in self._nodes:
            self._nodes[node_id] = {"label":label,"type":node_type}
            
        self._nodes[node_id].update(attrs)
        
    def add_edge(self, src:str,dst:str,relation:str,**attrs) -> None:
        if src not in self._nodes:
            raise ValueError(f"Sources node '{src}' not in the graph. Add it first")
        if dst not in self._nodes:
            raise ValueError(f"Destination node  '{dst}' not in graph . Add it first")
        
        if src not in self._edges:
            self._edges[src] = {}
            
        self._edges[src][dst] = {"relation": relation, **attrs}
        
        if dst not in self._in_edges:
            self._in_edges[dst] = []
            
        if src not in self._in_edges[dst]:
            self._in_edges[dst].append(src)
            

kg = KnowledgeGraph()
kg.add_node("company::apple", label="Apple", node_type="COMPANY")
kg.add_node("metric::apple::revenue", label="revenue", node_type="METRIC")
kg.add_edge("company::apple", "metric::apple::revenue", relation="HAS_METRIC")

print(kg._in_edges)
# def intialize_ingestion(file_path: str, company_name: str, doc_type:str = "10-k",fiscal_year: str = "FY2023"):
#     """
#         Orchestrates the ingestion , embedding , and storage.
#         Legacy BeautifulSoup  parsing replaced with layout-aware IBM Docling 
#     """
        
#     chroma_client = chromadb.PersistentClient(path="./chroma_db/")
        
#     collection = chroma_client.get_or_create_collection(name="financial_docs_v3",metadata={"hnsw:space":"cosine"})
        
#     model = SentenceTransformer('all-MiniLM-L6-v2')
        
#     if collection.count() > 0:
#         print(f"Cache hit:  found collection with {collection.count()} chunks. Skipping Docling parsing.")
            
#         stored_data = collection.get(include=["documents","metadatas"])
#         enriched_texts = stored_data["documents"]
        
#         chunks =[]
#         for meta, doc in zip(stored_data["metadatas"], stored_data["documents"]):
#             chunk_dict = meta.copy()
#             chunk_dict["text"] = doc
#             chunks.append(chunk_dict)
    
#     else:
#         print("Cache miss / first time run")
        
#         converter = DocumentConverter()
#         result = converter.convert(file_path)
        
#         tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
#         chunker = HybridChunker(tokenizer=tokenizer, max_tokens=256)
        
#         chunks = []
#         for i , docling_chunk in enumerate(chunker.chunk(result.document)):
#             text_content = docling_chunk.text.strip()
#             if not text_content or len(text_content) < 50:
#                 continue
            
#             heading_list = docling_chunk.meta.headings if docling_chunk.meta.headings else ["General  Document"]
#             section_title = heading_list[-1]
#             citation_path = ' > '.join(heading_list)
#             citation = f"{company_name} ({fiscal_year}) {doc_type} | {citation_path}"
            
#             chunks.append({
#                 "chunk_id":f"{company_name}_{fiscal_year}_chunk_{i}",
#                 "company": company_name,
#                 "doc_type":doc_type,
#                 "fiscal_year": fiscal_year,
#                 "section_title":section_title,
#                 "citation": citation,
#                 "text": text_content
#             })
        
#         print(f"✅ Docling parsing complete. Generated {len(chunks)} chunks.")
        
#         enriched_texts = [enrich_chunk_text(c) for c in chunks]
        
#         print("Generating heavy semantic embedding weights.... ")
#         embeddings = model.encode(enriched_texts, batch_size=32, show_progress_bar=True)
#         collection.add(
#             ids=[c["chunk_id"] for c in chunks],
#             embeddings=embeddings.tolist(),
#             documents=enriched_texts,
#             metadatas=[{k:  v for k , v in c.items() if k != 'text'} for c in chunks]
#         )
        
#     # 4. Shared High-Speed In-Memory BM25 Index Regeneration
#     tokenized_enriched = [text.lower().split() for text in enriched_texts]
#     bm25 = BM25Okapi(tokenized_enriched)

#     return {
#         "chunks": chunks,
#         "enriched_texts": enriched_texts,
#         "collection": collection,
#         "model": model,
#         "bm25": bm25
#     }