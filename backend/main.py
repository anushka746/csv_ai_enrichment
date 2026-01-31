"""
CSV Data Transformation API using Groq LLM
This FastAPI application processes CSV files and uses an LLM to generate
new columns based on existing data.
"""

import io
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse





allowed_origins = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5501").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)



@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {"message": "Upload your CSV at /upload_file to get it classified."}


@app.post("/upload_file")
async def process_csv(
    file: UploadFile = File(...),
    columns: str = Form(None),
    new_columns: str = Form(None)
):
    """Process CSV file and generate new columns using LLM."""
    
    try:    
       
        contents = await file.read()
        result = process_csv(contents, columns, new_columns)
        

        if not result["generated_anything"]:
           return JSONResponse(status_code=200,
                               content={
                                   "status": "no_change",
                                   "message": "CSV processed successfully, but no new values could be generated."})
           
        
        if result["partial_enrichment"]:
            return JSONResponse(status_code=200,
                                content={"status": "success",
                                         "message": "CSV processed successfully with partial enrichment."
                                         })
        
      
           
        
        
        output = io.StringIO()
        result["updated_df"].to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=updated.csv"}
        )
        
    except Exception as e:
        
        return JSONResponse(
            status_code=500,
            content={"status": "error", 
                     "message": "We couldn’t process this file due to an internal error. Please try again."}
        )
