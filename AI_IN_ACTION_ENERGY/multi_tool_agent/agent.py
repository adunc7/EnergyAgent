#Building the Agent 

import os
from time import time 
import certifi
import pymongo
from sqlalchemy import values
import vertexai
import re
 

from google.adk.agents import Agent 
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import load_artifacts

#from .import prompt

import google.genai.types as types
from vertexai.language_models import TextEmbeddingModel 
#from vertexai.vision_models import ImageGenerationModel



from dotenv import load_dotenv 
from google.adk import Agent 
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types 




import matplotlib.pyplot as plt


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
PROJECT_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CONNECTION_STRING = os.getenv("CONNECTION_STRING")

EMBEDDING_MODEL = "text-embedding-004" # 
IMG_MODEL = "imagen-3.0-generate-002" # Select the image generation model 

#Generate the embeddings for the query using VertexAI 

def generate_embeddings(query):
    vertexai.init(project=PROJECT_ID, location=PROJECT_LOCATION)
    model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
    return model.get_embeddings([query])[0].values
    

#-----------------------------------------------------------------------


# Solar Search - this function will take a natural language query and return the top matching solar descriptions from the MongoDB collection.
#Takes a natural language query and returns top matching descriptions
def search_solar(query: str) -> str:
    """Takes a natural language query and searches for solar energy potential data for a location at either the point or county level 
    """
    client = pymongo.MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
    vector_embeddings = generate_embeddings(query)

    #define pipeline 
    pipeline = [
        {
            "$vectorSearch": {
                "index": "energy_solar_vector_index",
                "path": "embedding",
                "queryVector": vector_embeddings,
                "numCandidates": 100,
                "limit": 2
            },
        },
        {
            "$project": {
                "_id": 0,
                "county": 1,
                "description": 1,
                "level":1,
                "latitude": {"$ifNull": ["$latitude", None]},
                "longitude": {"$ifNull": ["$longitude", None]},
                "embedding": 1,
                
            }
        }
    ]

    results = client[DATABASE_NAME][COLLECTION_NAME].aggregate(pipeline).to_list()

    return results

#-----------------------------------------------------------------------

def extract_labels_values(text: str)->str:
    """
    Extract labels and values from a natural language input string to use  for creating plots.
    Example input: "For A County, in 2022, the population is 50000. In B County, in 2022, the population is 60000."

      Returns:
        labels: List of label strings (e.g., ["A County", "B County"])
        values: List of integer values (e.g., [50000, 60000])
    """
    #pattern = r'([A-Za-z\s]+)\s+(\d+)'
    pattern = r'([A-Za-z\s]+County)[^\d]*(\d+)'
    matches = re.findall(pattern, text)
    labels = [label.strip() for label, value in matches]
    values = [int(value) for label, value in matches]
    return labels, values

  
#-----------------------------------------------------------------------
async def create_plots(text: str, tool_context: "ToolContext"):
    """
    Before generating the plot, ALWAYS ask the user to provide the counties they would like to compare, 
    as well as the metrics they would like to visualize.
    Use the extract_labels_values function to extract the labels and values from the text.
    available in matplotlib.pyplot as plt.
    Create a simple plot to visualize solar energy data using the tools to compare county values.
    Use only the county names on the xlabel.

    """
    labels, values = extract_labels_values(text)
    plt.figure()
    plt.bar(labels, values, color='skyblue')
    plt.title("Bar Graph")
    plt.xlabel("Category")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig("bar_plot.png")
    plt.close()

    with open("bar_plot.png", "rb") as f:
        image_bytes = f.read()

    
    image_artifact_1 = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    filename2 = "bar_plot.png"
    artifact2 =await tool_context.save_artifact(filename2, image_artifact_1)
    return artifact2

    
    


#-----------------------------------------------------------------------

MODEL = "gemini-2.0-flash"
#IMG_MODEL = "imagen-3.0-generate-002"

load_dotenv()

#Using the VertexAI client to generate images
client_google =Client(
    vertexai = True, 
    project = os.getenv("GOOGLE_CLOUD_PROJECT"),
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
                        
)

async def generate_image(prompt: str, tool_context: "ToolContext"):
    """Asks the user if thy would like to generate an image for science communication or marketing and which metrics county and 
    metric they would like to visualize. 
    "Create a simple graphic with the background as a high-resolution image of futuristic [City Name] 
    (e.g., Paris, San Diego, etc.). Use extract_labels_values to find ONLY numerical value.
    At the center, overlay a semi-transparent image box or card that 
    contains the value from extract_labels_values in bold text. The box should be centered
    and clearly visible, with clean,modern typography. 
    When the tool returns a file path, always format your response like this example: 
    Output is exactly: 'File saved as: "image8.png"'
    """

    response_img = client_google.models.generate_images(
        model=IMG_MODEL,
        prompt=prompt,
        config = {"number_of_images": 1}
    )

    if not response_img.generated_images:
        return {"status": "failed"}

    image_bytes = response_img.generated_images[0].image.image_bytes
    response_img.generated_images[0].image.save("image8.png")
   
    image_artifact = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    filename = "image8.png"
    await tool_context.save_artifact(filename, image_artifact)
    
    


#-----------------------------------------------------------------------

root_agent = Agent(
    model="gemini-2.0-flash",
    name="energy_agent",
    instruction=""" 
Start the Conversation with the user being a positive and friendly agent. 
Introduce yourself as the "Energy Explorer Agent" and ask user how can you help them today. 
You are an energy agent for a solar energy development company and you are here to help the user with their energy data understanding, comparing county level data, creating plots and generating sci comm or marketing images. 

Additional instructions:
1. Ask for details only if you don't understand the query and are not able to search.
2. You can use multiple tools in parallel by calling functions in parallel.
    """ ,
    tools=[
        search_solar, 
        extract_labels_values,
        create_plots,
        generate_image,
        load_artifacts
        
    ]
)
