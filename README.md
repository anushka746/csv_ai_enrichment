# CSV Data Transformation API

A FastAPI application that processes CSV files and uses Groq LLM to generate new columns based on existing data. This tool allows you to intelligently transform and enrich your CSV data using AI-powered column generation.

##  Features

- **AI-Powered Column Generation**: Use Groq LLM to generate new columns based on existing CSV data
- **Batch Processing**: Efficiently handle large datasets with configurable batch sizes
- **Selective Column Processing**: Choose specific columns to process or let the system auto-detect text columns
-  **Comprehensive Validation**: Built-in error handling for file size, column validation, and data integrity
- **Configurable**: Customize batch sizes, file limits, and LLM models via environment variables
- **Secure**: Environment-based configuration with proper `.gitignore` setup

## Quick Start

### Prerequisites

- Python 3.8 or higher
- A Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd csv
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

4. **Run the application**
   ```bash
   uvicorn backend.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

5. **Open the web interface**
   
   Open `index.html` in your browser (or serve it via a local server like Live Server)

## Usage

### Using the Web Interface

1. Open `index.html` in your browser
2. Drag and drop your CSV file or click to browse
3. Enter the source column name(s) you want to process (comma-separated)
4. Enter the new column name(s) you want to generate (comma-separated)
5. Click "Process CSV" and wait for the enhanced CSV to download

### Using the API Directly

#### POST `/upload_file`

Upload and process a CSV file.

**Request:**
- `file` (required): CSV file to upload
- `columns` (optional): Comma-separated list of columns to process. If not provided, all text columns will be processed.
- `new_columns` (optional): Comma-separated list of new column names to generate



**Response:**
- Success: CSV file with new columns (downloadable)
- Error: JSON response with error details

#### GET `/`

Returns API information.

```bash
curl http://localhost:8000/
```

##  Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | Your Groq API key | - |  Yes |
| `BATCH_SIZE` | Number of rows to process per batch | `50` | No |
| `MAX_FILE_SIZE_MB` | Maximum file size in MB | `10` | No |
| `LLM_MODEL` | Groq model to use | `llama-3.3-70b-versatile` | No |
| `CORS_ORIGINS` | Comma-separated list of allowed CORS origins | `http://127.0.0.1:5501` | No |

##  Project Structure

```
CSV/
├── backend/
│   ├── main.py           # FastAPI application and API endpoints
│   ├── prompt.py         # LLM prompt template for data transformation
│   ├── services.py 
│   ├──  config.py
│   └── __init__.py
│
├── frontend/
│   ├── index.html         # Web interface
│   ├── script.js          # Frontend JavaScript
│   └── style.css          # Frontend styles
│
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md              # This file

```

##  How It Works

1. **Upload**: User uploads a CSV file via the web interface or API
2. **Validation**: System validates file size, columns, and data integrity
3. **Batching**: Large files are split into configurable batch sizes
4. **LLM Processing**: Each batch is sent to Groq LLM with a carefully crafted prompt
5. **Transformation**: LLM generates new columns based on existing data
6. **Output**: Enhanced CSV is returned with original data plus new columns

##  Error Handling

The API provides detailed error messages for:
- ❌ File size limits exceeded
- ❌ Empty CSV files
- ❌ Missing or invalid columns
- ❌ Duplicate column names
- ❌ CSV parsing errors
- ❌ LLM API errors
- ❌ Data validation errors


##  Example

**Input CSV:**
```csv
name,description
Apple,"Fresh red apple"
Banana,"Yellow tropical fruit"
```

**Process with:**
- Source columns: `description`
- New columns: `category`

**Output CSV:**
```csv
name,description,category
Apple,"Fresh red apple","Fruit"
Banana,"Yellow tropical fruit","Fruit"
```



##  Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Groq](https://groq.com/) LLM
- Uses [Pandas](https://pandas.pydata.org/) for data processing

