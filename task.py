## Importing libraries and files
from crewai import Task
from crewai import LLM
from agents import financial_analyst, verifier
from tools import search_tool, FinancialDocumentTool,RiskTool,InvestmentTool

llm = LLM(
    model="huggingface/Qwen/Qwen2.5-72B-Instruct",   
    provider="huggingface"
)

if llm is None:
    raise RuntimeError("LLM not configured. Please instantiate your LLM client and assign to `llm`.")

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description=(
        "Analyze the uploaded financial document for the user's query: {query}. "
        "Extract key financial metrics such as revenue, net income, cash flow, liabilities, "
        "and margins. Identify notable trends and summarize them in a clear, data-backed way."
    ),

    expected_output=(
        "A structured analysis including:\n"
        "- Key extracted metrics (with values)\n"
        "- Observed trends (e.g., revenue growth/decline)\n"
        "- A concise summary of the company's financial health\n"
        "- Explicit statement of missing or unclear data"
    ),

    llm=llm,
    agent=financial_analyst,
    tools=[FinancialDocumentTool(),InvestmentTool(),RiskTool()],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description=(
        "Using the extracted financial data, provide general, non-personalized investment insights. "
        "Discuss possible implications for investors (e.g., revenue growth might suggest expansion, "
        "high debt could imply risk). Do NOT provide personalized financial advice."
    ),

    expected_output=(
        "A summary that includes:\n"
        "- Key financial ratios and their interpretations\n"
        "- Possible implications for investment outlook (general, not advice)\n"
        "- At least 3 clear caveats or limitations\n"
        "- Recommendation to consult a licensed professional for actionable advice"
    ),
    
    llm=llm,
    agent=financial_analyst,
    tools=[InvestmentTool()],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description=(
        "Assess the main financial risks of the company from the document. "
        "Focus on liquidity, leverage, market dependency, and operational risks. "
        "Clearly distinguish between high, medium, and low risk factors."
    ),

    expected_output=(
        "A structured risk assessment including:\n"
        "- Identified risks (liquidity, leverage, etc.)\n"
        "- Risk level categorization (low/medium/high)\n"
        "- Supporting evidence from the document\n"
        "- A summary of the most material risks"
    ),

    llm=llm,
    agent=financial_analyst,
    tools=[RiskTool()],
    async_execution=False,
)

    
verification = Task(
    description=(
        "Verify whether the uploaded file is a valid financial document. "
        "Check for financial terminology (e.g., 'Balance Sheet', 'Income Statement'), "
        "presence of numerical tables, and common structures of financial reports. "
        "Reject non-financial documents."
    ),

    expected_output=(
        "A structured verification result:\n"
        "- is_financial_document: True/False\n"
        "- Reasons for the decision\n"
        "- Key evidence (e.g., section headers, numbers)"
    ),

    llm=llm,
    agent=financial_analyst,
    tools=[FinancialDocumentTool()],
    async_execution=False
)