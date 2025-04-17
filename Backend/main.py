from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Set
import uvicorn
import os
import tempfile
import base64
import fitz  # PyMuPDF for checking if PDF has images
import google.generativeai as genai  # Google's Gemini API
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import re
import json
import requests
from urllib.parse import urljoin
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from basic1 import get_events



# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="SharePoint Content Extraction and Chat API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sophtimize.sharepoint.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI configuration


# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_FLASH_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# SharePoint configuration
SHAREPOINT_SITE_URL = os.getenv("SHAREPOINT_SITE_URL", "https://sophtimize.sharepoint.com/sites/GMFDemo")
SHAREPOINT_USERNAME = os.getenv("SHAREPOINT_USERNAME", "dhiraj.nehate@sophtimize.com")
SHAREPOINT_PASSWORD = os.getenv("SHAREPOINT_PASSWORD", "DnSph@2023")

# Global variable to store the thread ID for conversation
global_thread_id = None
# Global variable to store the vector store ID
vector_store_id = None

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ProcessContentRequest(BaseModel):
    process_site_pages: bool 
    process_documents: bool 
    store_name: str = "SharePoint Content"

# SharePoint authentication using UserCredential
def authenticate_sharepoint():
    try:
        credentials = UserCredential(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
        ctx = ClientContext(SHAREPOINT_SITE_URL).with_credentials(credentials)
        
        # Test the connection
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        print(f"Connected to SharePoint site: {web.properties['Title']}")
        return ctx
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None

# Fetch all pages from SitePages library
def fetch_all_sitepages():
    context = authenticate_sharepoint()
    if not context:
        return []
    
    pages = []
    try:
        # Get the SitePages library
        site_pages_library = context.web.lists.get_by_title("Site Pages")
        
        # Get items
        items = site_pages_library.items
        context.load(items)
        context.execute_query()
        
        for item in items:
            context.load(item, ["Title", "FileRef", "Modified", "FileLeafRef", "CanvasContent1"])
            context.execute_query()
            
            file_url = item.properties.get('FileRef')
            title = item.properties.get('Title', item.properties.get('FileLeafRef', 'No Title'))
            modified = item.properties.get('Modified', 'Unknown')
            
            # Try to get content directly from the CanvasContent1 field for modern pages
            canvas_content = item.properties.get('CanvasContent1', '')
            
            if file_url:
                page_info = {
                    'url': file_url,
                    'title': title,
                    'modified': modified,
                    'server_relative_url': file_url,
                    'canvas_content': canvas_content,
                    'absolute_url': urljoin(SHAREPOINT_SITE_URL, file_url)
                }
                pages.append(page_info)
                print(f"Found page: {title} - {file_url}")
    
    except Exception as e:
        print(f"Error in fetching site pages: {str(e)}")
    
    return pages

# Extract content from SharePoint pages
def extract_content_from_properties(page_info):
    if page_info.get('canvas_content'):
        try:
            # Parse the JSON content
            content_data = json.loads(page_info['canvas_content'])
            extracted_text = ""
            
            # Extract text from each control in the canvas
            if isinstance(content_data, dict) and 'controlData' in content_data:
                for control_key, control in content_data['controlData'].items():
                    if isinstance(control, dict):
                        # Extract text from text controls
                        if 'innerHTML' in control:
                            html_content = control['innerHTML']
                            soup = BeautifulSoup(html_content, 'html.parser')
                            extracted_text += soup.get_text(separator=' ', strip=True) + "\n\n"
            
            return extracted_text.strip()
        except (json.JSONDecodeError, TypeError):
            # If it's not JSON or has parsing issues
            soup = BeautifulSoup(page_info['canvas_content'], 'html.parser')
            return soup.get_text(separator=' ', strip=True)
    
    return None

# Get page content using SharePoint Client API
def get_page_content_api(page_info):
    try:
        # Create an authenticated session
        context = authenticate_sharepoint()
        if not context:
            return None
        
        # Get the file object
        file_obj = context.web.get_file_by_server_relative_url(page_info['server_relative_url'])
        
        # Get modern page content
        list_item = file_obj.listItemAllFields
        context.load(list_item, ["CanvasContent1", "WikiField"])
        context.execute_query()
        
        # Try modern page content first
        if hasattr(list_item, 'properties') and 'CanvasContent1' in list_item.properties:
            canvas_content = list_item.properties['CanvasContent1']
            if canvas_content:
                try:
                    # Parse the JSON content
                    content_data = json.loads(canvas_content)
                    extracted_text = ""
                    
                    # Extract text from each control in the canvas
                    if isinstance(content_data, dict) and 'controlData' in content_data:
                        for control_key, control in content_data['controlData'].items():
                            if isinstance(control, dict):
                                # Extract text from text controls
                                if 'innerHTML' in control:
                                    html_content = control['innerHTML']
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    extracted_text += soup.get_text(separator=' ', strip=True) + "\n\n"
                    
                    return extracted_text.strip()
                except (json.JSONDecodeError, TypeError):
                    # If it's not JSON or has parsing issues
                    soup = BeautifulSoup(canvas_content, 'html.parser')
                    return soup.get_text(separator=' ', strip=True)
        
        # Try wiki field for classic pages
        if hasattr(list_item, 'properties') and 'WikiField' in list_item.properties:
            wiki_content = list_item.properties['WikiField']
            if wiki_content:
                soup = BeautifulSoup(wiki_content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
        
        return None
    except Exception as e:
        print(f"Error getting page content via API: {str(e)}")
        return None

# Process pages and extract content
def process_pages(pages):
    processed_pages = []
    
    for page in pages:
        print(f"\nProcessing page: {page['title']}")
        
        # Try methods until we get content
        content = None
        
        # Method 1: Check if we already have canvas content
        if not content:
            print("Trying to extract content from page properties...")
            content = extract_content_from_properties(page)
            if content:
                print("Successfully extracted content from page properties.")
        
        # Method 2: Try the SharePoint Client API
        if not content:
            print("Trying to get content using SharePoint Client API...")
            content = get_page_content_api(page)
            if content:
                print("Successfully extracted content using SharePoint Client API.")
        
        # If we have content, add it to the results
        if content:
            # Clean up content
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\n+', '\n', content)
            content = content.strip()
            
            processed_pages.append({
                'title': page['title'],
                'url': page['server_relative_url'],
                'content': content,
                'modified': page.get('modified', 'Unknown')
            })
            
            print(f"Successfully extracted content from {page['title']} ({len(content)} characters)")
        else:
            print(f"Failed to extract content from {page['title']} using all methods")
    
    return processed_pages

# Save extracted text content to files
def save_text_contents(processed_pages, output_dir="extracted_text"):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    
    for page in processed_pages:
        # Create a safe filename
        safe_title = re.sub(r'[^\w\-_]', '_', page['title'])
        filename = os.path.join(output_dir, f"{safe_title}.txt")
        
        # Write content to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Title: {page['title']}\n")
            f.write(f"URL: {page['url']}\n")
            f.write(f"Modified: {page['modified']}\n")
            f.write("-" * 80 + "\n\n")
            f.write(page['content'])
        
        saved_files.append(filename)
        print(f"Saved text content to {filename}")
    
    return saved_files

# Fetch all documents from SharePoint
def fetch_all_sharepoint_documents():
    context = authenticate_sharepoint()
    if not context:
        return []
    
    # List of potential document library paths to try
    doc_lib_paths = [
        "Shared Documents",
        "Documents"
    ]
    
    documents = []
    
    # Try each document library path
    for path in doc_lib_paths:
        try:
            print(f"Trying to access: {path}")
            relative_url = f"/sites/GMFDemo/{path}"  # Should be parameterized in production
            
            # Check if path exists as a folder
            try:
                folder = context.web.get_folder_by_server_relative_url(relative_url)
                context.load(folder)
                context.execute_query()
                print(f"Successfully accessed folder: {path}")
                
                # Get files from folder
                files = folder.files
                context.load(files)
                context.execute_query()
                
                # Skip if no files are found in this folder
                if not files:
                    print(f"No files found in folder: {path}. Skipping...")
                    continue
                
                # Add the files to the documents list
                for file in files:
                    file_url = file.properties.get('ServerRelativeUrl')
                    if file_url:
                        documents.append(file_url)
                
                print(f"Found {len(documents)} files in {path}")
                
            except Exception as folder_error:
                print(f"Error accessing folder {path}: {str(folder_error)}")
                
                # Try as a document library
                try:
                    doc_lib = context.web.lists.get_by_title(path.split('/')[-1])
                    items = doc_lib.items
                    context.load(items)
                    context.execute_query()
                    
                    # Skip if no files are found in this document library
                    if not items:
                        print(f"No files found in document library: {path}. Skipping...")
                        continue
                    
                    # Add the files to the documents list
                    for item in items:
                        file_url = item.properties.get('FileRef')
                        if file_url:
                            documents.append(file_url)
                    
                    print(f"Found {len(documents)} files in document library {path}")
                except Exception as lib_error:
                    print(f"Error accessing document library {path}: {str(lib_error)}")
                    
        except Exception as e:
            print(f"Error with path {path}: {str(e)}")
    
    return documents

# Download files from SharePoint and save to temp directory
def download_sharepoint_files(file_urls):
    context = authenticate_sharepoint()
    if not context:
        return [], None
        
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    
    for file_url in file_urls:
        try:
            # Get the file using server relative URL
            file = context.web.get_file_by_server_relative_url(file_url)
            context.load(file)
            context.execute_query()
            
            # Extract file name from the URL
            file_name = file_url.split('/')[-1]
            local_path = os.path.join(temp_dir, file_name)
            
            # Download file content
            with open(local_path, 'wb') as local_file:
                file_content = File.open_binary(context, file_url)
                local_file.write(file_content.content)
            
            saved_files.append(local_path)
            print(f"Downloaded: {file_name}")
            
        except Exception as e:
            print(f"Error downloading {file_url}: {str(e)}")
    
    return saved_files, temp_dir

# Check if PDF contains images
def pdf_contains_images(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        for page in pdf_document:
            image_list = page.get_images(full=True)
            if image_list:
                pdf_document.close()
                return True
        pdf_document.close()
        return False
    except Exception as e:
        print(f"Error checking for images in {pdf_path}: {str(e)}")
        return False

# Process PDF with Gemini
def process_pdf_with_gemini(pdf_path):
    try:
        # Read PDF file and encode it to Base64
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        pdf_data = base64.b64encode(pdf_bytes).decode("utf-8")
        
        # Initialize Gemini model
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Define extraction prompt
        extract_prompt = (
            "Extract all text the attached PDF. "
            "Format your response as a well-structured markdown document. "
            "Include detailed descriptions of charts, diagrams, and any visual elements. "
            "Organize content by page and section where appropriate."
        )
        
        # Call Gemini to extract text and analyze images
        response = gemini_model.generate_content(
            contents=[
                {"mime_type": "application/pdf", "data": pdf_data},
                {"text": extract_prompt}
            ],
            generation_config={"temperature": 0.1}
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error processing PDF with Gemini: {str(e)}")
        return None

# Create markdown file from Gemini's response
def create_markdown_from_pdf_analysis(pdf_path, content):
    if not content:
        return None
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    markdown_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}.md")
    
    try:
        with open(markdown_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# PDF Analysis: {base_name}\n\n")
            md_file.write(content)
        
        print(f"Created markdown file: {markdown_path}")
        return markdown_path
    
    except Exception as e:
        print(f"Error creating markdown file for {pdf_path}: {str(e)}")
        return None

# Process PDFs that contain images and track processed PDFs
def process_pdfs_with_gemini(file_paths):
    additional_files = []
    processed_pdfs = set()  # Track PDFs that have been processed
    
    for file_path in file_paths:
        # Check if the file is a PDF
        if file_path.lower().endswith('.pdf'):
            # Check if PDF contains images
            if pdf_contains_images(file_path):
                print(f"Processing PDF with images: {os.path.basename(file_path)}")
                
                # Process entire PDF with Gemini
                analysis_content = process_pdf_with_gemini(file_path)
                
                # Create markdown file from analysis
                if analysis_content:
                    markdown_file = create_markdown_from_pdf_analysis(file_path, analysis_content)
                    if markdown_file:
                        additional_files.append(markdown_file)
                        # Add this PDF to the list of processed PDFs
                        processed_pdfs.add(file_path)
            else:
                print(f"PDF does not contain images, skipping: {os.path.basename(file_path)}")
    
    return additional_files, processed_pdfs

# Create vector store and upload files
def create_vector_store_with_files(files, store_name="SharePoint Documents"):
    global vector_store_id
    
    # Create a new vector store
    vector_store = openai_client.vector_stores.create(name=store_name)
    vector_store_id = vector_store.id
    
    # Open files and upload to vector store
    file_streams = []
    
    try:
        # Open all files
        for path in files:
            file_streams.append(open(path, "rb"))
        
        file_batch = openai_client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=file_streams
        )
        
        print(f"Vector store upload status: {file_batch.status}")
        print(f"File counts: {file_batch.file_counts}")
        
        return vector_store.id
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None
    finally:
        # Ensure all file streams are closed
        for stream in file_streams:
            stream.close()

# Update assistant with vector store
def update_assistant_with_vector_store(assistant_id, vector_store_id):
    try:
        # Update the assistant with the vector store
        assistant = openai_client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}} 
        )
        print(f"Assistant updated with vector store: {vector_store_id}")
        return assistant
    except Exception as e:
        print(f"Error updating assistant: {str(e)}")
        return None

# Initialize a thread for chat
def initialize_chat_thread():
    global global_thread_id
    try:
        thread = openai_client.beta.threads.create()
        global_thread_id = thread.id
        print(f"Created new conversation thread: {thread.id}")
        return thread.id
    except Exception as e:
        print(f"Error creating thread: {str(e)}")
        return None

# Get or create thread ID
def get_thread_id():
    global global_thread_id
    if not global_thread_id:
        global_thread_id = initialize_chat_thread()
    return global_thread_id

# Process chat message and get response
def process_chat_message(message: str):
    thread_id = get_thread_id()
    if not thread_id:
        raise HTTPException(status_code=500, detail="Failed to create chat thread")
    
    try:
        # Add user message to thread
        openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Run the assistant
        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Get the latest message (the assistant's response)
        messages = list(openai_client.beta.threads.messages.list(thread_id=thread_id))
        assistant_message = messages[0]  # Latest message
        
        if assistant_message.role == "assistant" and assistant_message.content:
            content = assistant_message.content[0].text
            return content.value
        else:
            return "No response received from assistant."
    except Exception as e:
        print(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# API endpoint to process SharePoint content
@app.post("/process-content")
async def process_content(request: ProcessContentRequest):
    try:
        all_files = []
        
        # Process site pages if requested
        if request.process_site_pages:
            print("Processing SharePoint site pages...")
            pages = fetch_all_sitepages()
            if pages:
                processed_pages = process_pages(pages)
                page_files = save_text_contents(processed_pages)
                all_files.extend(page_files)
                print(f"Processed {len(processed_pages)} site pages")
            else:
                print("No site pages found to process")
        
        # Process SharePoint documents if requested
        if request.process_documents:
            print("Processing SharePoint documents...")
            document_urls = fetch_all_sharepoint_documents()
            if document_urls:
                local_files, temp_dir = download_sharepoint_files(document_urls)
                
                # Process PDFs containing images with Gemini
                print("Processing PDFs with images using Gemini...")
                additional_files, processed_pdfs = process_pdfs_with_gemini(local_files)
                
                # Only include files that weren't processed into markdown (to avoid duplicates)
                files_to_process = []
                for file_path in local_files:
                    if file_path in processed_pdfs:
                        print(f"Skipping original PDF in favor of markdown: {os.path.basename(file_path)}")
                        continue
                    else:
                        files_to_process.append(file_path)
                
                # Add both regular files and markdown files
                all_files.extend(files_to_process)
                all_files.extend(additional_files)
                print(f"Processed {len(document_urls)} documents")
            else:
                print("No documents found to process")
        
        # Create vector store with all files if any files were processed
        if all_files:
            print(f"Creating vector store with {len(all_files)} files...")
            vector_store_id = create_vector_store_with_files(all_files, request.store_name)
            
            if vector_store_id:
                print("Updating assistant with vector store...")
                assistant = update_assistant_with_vector_store(ASSISTANT_ID, vector_store_id)
                
                if assistant:
                    # Initialize a new thread for chat
                    thread_id = initialize_chat_thread()
                    return {"status": "success", "message": f"Processed {len(all_files)} files and updated assistant", "vector_store_id": vector_store_id, "thread_id": thread_id}
                else:
                    return {"status": "error", "message": "Failed to update assistant with vector store"}
            else:
                return {"status": "error", "message": "Failed to create vector store"}
        else:
            return {"status": "error", "message": "No files were processed"}
    
    except Exception as e:
        print(f"Error in process_content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if not vector_store_id:
            return JSONResponse(
                status_code=400,
                content={"error": "No content has been processed yet. Please call /process-content first."}
            )
        querflag = query_flag(request.message)
        print("flag =", querflag)
        
        response = ""
        
        
        if querflag == "False":
           response = process_chat_message(request.message)
        if querflag == "True":
           response_event = get_events()  
           print("testing",response_event)
           response= Event_method(request.message,response_event)
        if querflag == "Donation":
            response= ask_about_donor(request.message)  
            
        
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
def query_flag(question):
    # Send the request to OpenAI's model using the OpenAI client
    prompt= f"""Analyze the user query: {question}

            Classify its primary focus:
            * **Event** (meeting,reminder, etc.)
            * **Donation** (Donors,Campaign,donations etc.)

            Output ONLY a boolean:`True` if Event ,`Donation` if Donation , `False` if other,. No other text."""
            
    response = openai_client.chat.completions.create(  # Updated method calls
        model="gpt-4o-mini",  # You can change this to any model available
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=15000,  # Limit the response length (adjust as needed)
        temperature=0.7   # Adjust the creativity of the response
    )

    # Extract and return the response text (updated to match new response format)
    return response.choices[0].message.content.strip()


    
def Event_method(question,data):
    # Send the request to OpenAI's model using the OpenAI client
    prompt= f"""You are an AI assistant. Your task is to answer a user's query based *strictly* and *only* on the provided event data. Do not use any external knowledge or make assumptions beyond what is explicitly stated in the data.
 
    Here is the event data:
    {data}
    User Query: "{question}"
 
    Based *only* on the event data provided above, answer the user's query. Format your response clearly and appropriately for the query. For example, if the query asks for a list, provide a list. If it asks for details of one event, provide those details. If no events match the query, state that clearly. Clean up any HTML tags (like <p>) in descriptions when presenting them."""
            
    response = openai_client.chat.completions.create(  # Updated method call
        model="gpt-4o-mini",  # You can change this to any model available
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=15000,  # Limit the response length (adjust as needed)
        temperature=0.7   # Adjust the creativity of the response
    )

    # Extract and return the response text (updated to match new response format)
    return response.choices[0].message.content.strip()

def ask_about_donor(question):
        # Load CSV into a pandas DataFrame
    df = pd.read_csv("Updated_Donations_data.csv")
    
    # Convert DataFrame to a string representation
    df_string = df.to_string()
    
    prompt= f"""You are an AI assistant. Your task is to answer a user's query based *strictly* and *only* on the provided donor data. Do not use any external knowledge or make assumptions beyond what is explicitly stated in the data.
 
    Here is the Donor data:
    { df_string }
    User Query: "{question}"
 
    Based *only* on the donor data provided above, answer the user's query. Format your response clearly and appropriately for the query. For example, if the query asks for a list, provide a list. If it asks for details of one donor, provide those details. If no donors match the query, state that clearly.in descriptions when presenting them
    provide Coorect output always Normal Text format"""
           
    
    # Make the API call with the data and question
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",  # Use an appropriate model
        messages=[
            # {"role": "system", "content": "You are analyzing a pandas DataFrame. Here's the data:\n" + df_string},
            {"role": "user", "content": prompt }
        ]
    )
    
    # Return the response message content
    return response.choices[0].message.content




# Root endpoint for health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "SharePoint Content and Chat API is running"}

# Startup event to load environment variables and initialize clients
@app.on_event("startup")
async def startup_event():
    load_dotenv()
    print("FastAPI SharePoint Content Extraction and Chat API started")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)