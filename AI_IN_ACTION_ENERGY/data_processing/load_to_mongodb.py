import json 
from pymongo import MongoClient 
from dotenv import load_dotenv
import os

#from google.cloud import aiplatform
#import vertexai
#from vertexai.language_models import TextEmbeddingModel
#import vertexai.language_models
import vertexai
from vertexai.language_models import TextEmbeddingModel
load_dotenv()



#---Configuration---#
JSON_FILE = os.getenv("JSON_FILE")  # Path to the JSON file containing solar summaries/descriptions
PROJECT = os.getenv("PROJECT")
REGION = os.getenv("REGION")
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

MODEL = "text-embedding-004"

#---Initializeze Vertex AI (Gemini)---#
vertexai.init(project = PROJECT, location = REGION )

embedding_model = TextEmbeddingModel.from_pretrained(MODEL)



# Function to load JSON data and generate embeddings for each document
def generate_embeddings(json_path):
    with open(json_path, 'r',encoding ='utf-8') as f: 
        data =json.load(f)

    for doc in data:
        text = doc.get("description", "")
        #embedding = embedding_model.get_embeddings([text])[0].values
       # embedding = embedding_model.get_embeddings([text])[0].values  # Get the embedding for the text
        embedding = embedding_model.get_embeddings([text])[0].values
        doc["embedding"] = embedding
    return data

#Try with one point first 

def upload_to_mongodb(docs):
    client= MongoClient(MONGODB_URI)
    db  = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    #Optional: clear existing data 
    collection.delete_many({})

    collection.insert_many(docs) #  insert indivdually.

    print(f"Uploaded {len(docs)} documents into MongoDB collection '{COLLECTION_NAME}' in database '{DB_NAME}'.")



#-----------Test with a smaller file size first-----------#


#---Run the pipeline--# 
if __name__ == "__main__":

    # Do not test with the larger file first, test with smaller file to ensure embeddings working.
    docs = generate_embeddings(JSON_FILE)  
    upload_to_mongodb(docs)
    print("Data loading and embedding generation completed successfully.")