## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()


from crewai import Agent,LLM

from tools import search_tool, FinancialDocumentTool,InvestmentTool,RiskTool

### Loading LLM
llm = LLM(
    model="huggingface/Qwen/Qwen2.5-72B-Instruct",   
    provider="huggingface"
)

if llm is None:
    raise RuntimeError("LLM not configured. Please instantiate your LLM client and assign to `llm`.")

financial_doc_tool = FinancialDocumentTool()
investment_tool = InvestmentTool()
risk_tool = RiskTool()
# Creating an Experienced Financial Analyst agent
financial_analyst=Agent(
    role="Senior Financial Analyst (analytical, evidence-first)",
    goal=(
        "Accurately analyze the provided financial document, extract key metrics (revenue, net income, "
        "margins, cash flow), identify discrepancies, and summarize findings. "
        "If a question requires judgement or regulated financial advice, clearly state limitations "
        "and recommend consulting a licensed financial professional."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst whose priority is accuracy and transparency. "
        "You cite sources when possible and explicitly state uncertainty. "
        "Do not invent facts; if a value is missing, ask for clarification or say 'insufficient data'."
    ),
    tools=[financial_doc_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=True  # Allow delegation to other specialists
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Verify whether the uploaded file is a financial document: check format, required fields, and "
        "evidence of financial data (numeric fields, tables with amounts, headers such as 'Balance Sheet', 'Income Statement'). "
        "If the document is not a financial report, respond with a concise rejection and explain why."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are meticulous and compliance-focused. Your job is to determine whether a document qualifies "
        "as a financial report for downstream analysis; if unsure, request clarification or reject."
    ),
    tools=[investment_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=True
)


investment_advisor = Agent(
    role="Investment Advisor (informational, non-regulated)",
    goal=(
        "Provide general, non-actionable investment information derived from the document and public sources. "
        "Do NOT give personalized or regulated financial advice. When offering options, present risks, and "
        "cite the basis (document + public data). Recommend seeking licensed financial advice for decisions."
    ),
    verbose=True,
    backstory=(
        "You provide evidence-based, balanced descriptions of investment options, explicitly noting uncertainty, "
        "risks, and that recommendations are informational only."
    ),
    tools=[investment_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)


risk_assessor = Agent(
    role="Extreme Risk Assessment Expert",
    goal=(
        "Identify and explain material risk factors in the document (liquidity risk, leverage, concentration, "
        "revenue reliability). Provide a reasoned risk summary and quantify where possible. Avoid hyperbole; "
        "state assumptions and cite document lines/sections used."
    ),
    verbose=True,
    backstory=(
        "You are conservative and evidence-focused. You quantify risks when possible and clearly mark subjective judgements."
    ),
    tools=[risk_tool],
    llm=llm,
    max_iter=1,
    max_rpm=1,
    allow_delegation=False
)
