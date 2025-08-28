# 📊 Financial Document Analyzer API

This project provides a backend API for **analyzing financial documents (PDFs)** using **CrewAI agents** and Hugging Face models. It allows uploading a financial report (e.g., *Tesla quarterly report*), running multiple agents (financial analyst, verifier, investment advisor, risk assessor), and returning structured investment insights.

-----

## 🐞 Bugs Found & Fixes

### 1\. Invalid File Path for Tool

  * **Bug:** The CrewAI `Financial Document Reader` tool was receiving `"uploaded_financial_document.pdf"` instead of the actual saved file path.
  * **Fix:**
      * Changed file handling to save the uploaded file in `data/{uuid}.pdf`.
      * Passed the **absolute local file path** to CrewAI tools.

-----

### 2\. File Not Found / Cleanup Issue

  * **Bug:** Uploaded files were not cleaned up, leading to clutter.
  * **Fix:**
      * Added a `finally` block to safely remove files after analysis.
      * Wrapped cleanup with exception handling to avoid masking errors.

-----

### 3\. Hugging Face API Errors Returning 500

  * **Bug:** Hugging Face model errors only returned `"500 Internal Server Error"` with no details.
  * **Fix:**
      * Added structured error handling in `/analyze`.
      * Logs **traceback** and returns `"422 - Hugging Face API request failed"` if an API error is detected.

-----

### 4\. File Size Handling

  * **Bug:** Large file uploads (\>10MB) could crash the app.
  * **Fix:**
      * Added streaming file writes in **1MB chunks**.
      * Hard limit: `10 MB` → returns **413 Payload Too Large**.

-----

### 5\. CrewAI Async vs Sync Kickoff

  * **Bug:** CrewAI sometimes returned sync results and sometimes coroutines, leading to `await` errors.
  * **Fix:**
      * Added a helper `maybe_await()` that works with both sync and async return values.

-----

## ⚙️ Setup & Usage Instructions

### 1\. Clone Repository

```bash
git clone https://github.com/yourusername/financial-document-analyzer.git
cd financial-document-analyzer
```

-----

### 2\. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

-----

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

-----

### 4\. Setup Environment Variables

Create a `.env` file in the project root and add:

```bash
HUGGINGFACE_API_KEY=your_hf_api_key_here
```

-----

### 5\. Run the Server

```bash
uvicorn app:app --reload
```
API will be live at:
👉 http://localhost:8000

-----

## 📡 API Documentation

**Base URL**
`http://localhost:8000`

### Endpoints

1.  **Health Check**

      * `GET /`
      * **Response**
        ```json
        {
          "message": "Financial Document Analyzer API is running"
        }
        ```

2.  **Analyze Financial Document**

      * `POST /analyze`
      * **Form Data**
          * `file`: PDF file (required, max 10MB)
          * `query`: Analysis query (optional, default = "Analyze this financial document for investment insights")
    
        ```
      * **Example Response**
        ```json
        {
          "status": "success",
          "query": "Summarize the investment risks in this document",
          "analysis": "...analysis result here...",
          "file_processed": "TSLA.pdf"
        }
        ```

-----


## 📂 Project Structure

```
financial-document-analyzer/
│── main.py               # Application entrypoint (starts FastAPI server)
│── agents.py             # CrewAI agent definitions
│── task.py               # CrewAI tasks
│── tools.py              # Utility tools (e.g., document reader, parsers)
│── requirements.txt      # Python dependencies
│── .env                  # Environment variables (not committed)
│── data/                 # Temporary uploaded PDFs

```

-----

## 🛠 Tech Stack

  * **Backend:** FastAPI
  * **AI Orchestration:** CrewAI
  * **LLM Provider:** Hugging Face
  * **Server:** Uvicorn
  * **Language:** Python 3.10+

-----
