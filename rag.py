from ollama import Client
import json
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

client = chromadb.PersistentClient()
remote_client = Client(host=f"http://localhost:11434")
collection = client.get_or_create_collection(name="articles_demo")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20, separators=["."]
)

try:
    with open("counter.txt", "r") as f:
        count = int(f.read().strip())
except FileNotFoundError:
    count = 0

if not os.path.exists("chroma") or collection.count() == 0:
    print("Reading articles.jsonl and generating embeddings...")
    with open("articles.jsonl", "r") as f:
        for i, line in enumerate(f):
            if i < count:
                continue
            article = json.loads(line)
            content = article["description"]
            sentences = text_splitter.split_text(content)

            for chunk_index, each_sentence in enumerate(sentences):
                response = remote_client.embed(model="nomic-embed-text", input=f"search_document: {each_sentence}")
                embedding = response["embeddings"][0]

                collection.add(
                    ids=[f"article_{i}_chunk_{chunk_index}"],
                    embeddings=[embedding],
                    documents=[each_sentence],
                    metadatas=[{"title": article["title"]}],
                )
        
        with open("counter.txt", "w") as f:
            f.write(str(i + 1))
    
    print("Database built successfully!")

query = "Who is set to win the election ?"
query_embed = remote_client.embed(model="nomic-embed-text", input=f"query: {query}")["embeddings"][0]
results = collection.query(query_embeddings=[query_embed], n_results=1)

print(f"\nQuestion: {query}")
print(f'\nTitle: {results["metadatas"][0][0]["title"]} \n{results["documents"][0][0]}')