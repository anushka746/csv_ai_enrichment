import os
import io
import json
import pandas as pd
from fastapi.responses import JSONResponse
from backend.prompt import PROMPT_TEMPLATE
from backend.config import client,MAX_FILE_SIZE_BYTES,BATCH_SIZE,LLM_MODEL,MAX_FILE_SIZE_MB





def chunk_list(lst, chunk_size):
    """Split a list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
        
        
def process_csv(contents: bytes, columns: str = None, new_columns: str = None):
    try:
        
       
        if len(contents) > MAX_FILE_SIZE_BYTES:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB"
                }
            )
        
        csv_text = contents.decode("utf-8")
        
        df = pd.read_csv(io.StringIO(csv_text))
     
        if df.empty:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "The CSV is empty, no rows to process"}
            )
        
        df = df.reset_index(drop=True)
        df["__row_id__"] = df.index
        
        existing_columns = df.columns.tolist()
        if columns:
            col_to_process = [column.strip() for column in columns.split(",")]
        else:
            col_to_process = df.select_dtypes(include='object').columns.tolist()
        
        missing_cols = [col for col in col_to_process if col not in df.columns.tolist()]
        if missing_cols:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"The following source columns do not exist in the CSV: {', '.join(missing_cols)}"
                }
            )
        
        duplicates = df.columns[df.columns.duplicated()].tolist()
        if duplicates:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"CSV contains duplicate columns: {', '.join(duplicates)}"
                }
            )
        
        if not col_to_process:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No columns to process"}
            )
        
        df[col_to_process] = df[col_to_process].fillna("")
        
        if new_columns:
            user_defined_columns = [col.strip() for col in new_columns.split(",")]
        else:
            user_defined_columns = []
       
        batch_size = BATCH_SIZE
        
        all_results = []
        row_data = df[col_to_process + ["__row_id__"]].to_dict(orient="records")
        batches = list(chunk_list(row_data, batch_size))
        
        for idx, batch in enumerate(batches):
            prompt = PROMPT_TEMPLATE.format(
                batch=json.dumps(batch, indent=2),
                user_defined_columns=user_defined_columns
            )
            
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            output_text = response.choices[0].message.content
            clean = output_text.replace("```", "").strip()
            print(clean)
            
            try:
                result = json.loads(clean)
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=500,
                    content={
                            "status": "error",
                            "detail":"AI response format error",
                            "message": "The model returned malformed data for one of the batches. Please simplify column names or retry."
                             })
    
            # Ensure result is a list of dict
            if not isinstance(result, list) or not all(isinstance(r, dict) for r in result):
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "detail":"AI response format error",
                        
                        "message": "The AI model returned data in an unexpected format."
                        })
                
            model_rows = {r["__row_id__"]: r for r in result if "__row_id__" in r}
            normalized_rows = []
            for row in batch:
                rid = row["__row_id__"]
                if rid in model_rows:
                    normalized_rows.append(model_rows[rid])
                else:
                    normalized_rows.append({
                        "__row_id__": rid,
                        **{col: None for col in user_defined_columns}
                        })


    
          
                
            all_results.extend(normalized_rows)
    
        
        df = df.drop(columns=["__row_id__"])
        new_df = pd.DataFrame(all_results).drop(columns=["__row_id__"])
        updated = pd.concat([df, new_df], axis=1)
        generated_anything = (new_df[user_defined_columns]
        .replace(r"^\s*$", pd.NA, regex=True)                    
        .notna()
        .any()
        .any())
        
        non_empty_columns = (new_df[user_defined_columns]
                             .replace(r"^\s*$", pd.NA, regex=True)
                             .notna()
                             .any()
                             )
        return {
        "updated_df": updated,
        "generated_anything": generated_anything,
        "partial_enrichment": (
            non_empty_columns.any() and not non_empty_columns.all()
        )
    }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"}
        )