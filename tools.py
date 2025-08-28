## Importing libraries and files
import os
import json
from abc import ABC
import re
from dotenv import load_dotenv
import statistics
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

from crewai_tools import tools
from crewai_tools import SerperDevTool
from crewai.tools import BaseTool,tool

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool(BaseTool, ABC):
    name: str = "Financial Document Reader"
    description: str = "Reads and cleans financial documents (PDF). Returns JSON string with full text and page breakdown."
    def _run(self, path: str = "data/sample.pdf") -> str:
        """Read and clean a PDF financial document.

        Args:
            path (str, optional): Path to the PDF file.

        Returns:
            str: JSON string with "pages" and "full_text".
        """
        loader = PyPDFLoader(path)
        docs = loader.load()

        pages = []
        full_report = []
        for i, data in enumerate(docs, start=1):
            content = data.page_content.replace("\n\n", "\n")
            pages.append({"page": i, "content": content})
            full_report.append(content)

        result = {
            "pages": pages,
            "full_text": "\n".join(full_report)
        }

        return json.dumps(result, indent=2)

    async def _arun(self, path: str = "data/sample.pdf") -> str:
        """Async version of _run (required by BaseTool)."""
        return self._run(path)

## Creating Investment Analysis Tool
class InvestmentTool(BaseTool, ABC):
    name: str = "Investment Analysis Tool"
    description: str = "Analyzes financial document data for investment insights."

    def _run(self, financial_document_data: str) -> str:
        """
        Analyze cleaned financial document data for investment insights.
        """

        # === Step 1: Basic text cleanup ===
        processed_data = " ".join(financial_document_data.split())

        # === Step 2: Extract financial numbers (simple regex for $, %, etc.) ===
        revenue_matches = re.findall(r"revenue[s]?\s+[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)
        profit_matches = re.findall(r"(net income|profit)[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)
        debt_matches = re.findall(r"(debt|liabilities)[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)

        revenues = [float(r.replace(",", "")) for r in revenue_matches if r.replace(",", "").isdigit()]
        profits = [float(p[1].replace(",", "")) for p in profit_matches if p[1].replace(",", "").isdigit()]
        debts = [float(d[1].replace(",", "")) for d in debt_matches if d[1].replace(",", "").isdigit()]

        # === Step 3: Calculate basic ratios if data exists ===
        insights = []
        if revenues and profits:
            avg_revenue = statistics.mean(revenues)
            avg_profit = statistics.mean(profits)
            profit_margin = (avg_profit / avg_revenue) * 100 if avg_revenue else 0
            insights.append(f"📊 Average Revenue: ${avg_revenue:,.2f}")
            insights.append(f"📊 Average Profit: ${avg_profit:,.2f}")
            insights.append(f"📊 Profit Margin: {profit_margin:.2f}%")

        if debts and profits:
            avg_debt = statistics.mean(debts)
            debt_to_income = (avg_debt / statistics.mean(profits)) if profits else 0
            insights.append(f"⚖️ Avg Debt: ${avg_debt:,.2f}")
            insights.append(f"⚖️ Debt-to-Income Ratio: {debt_to_income:.2f}")

        # === Step 4: Sentiment cues (very basic keyword analysis) ===
        positive_keywords = ["growth", "expansion", "profit", "strong", "increase", "positive"]
        negative_keywords = ["loss", "decline", "risk", "decrease", "negative", "litigation"]

        positive_hits = sum(processed_data.lower().count(word) for word in positive_keywords)
        negative_hits = sum(processed_data.lower().count(word) for word in negative_keywords)

        if positive_hits > negative_hits:
            sentiment = "✅ Positive financial outlook detected."
        elif negative_hits > positive_hits:
            sentiment = "⚠️ Negative financial risks detected."
        else:
            sentiment = "ℹ️ Neutral outlook."

        insights.append(sentiment)

        # === Step 5: Investment Recommendation ===
        recommendation = "Hold"
        if profits and revenues:
            margin = (statistics.mean(profits) / statistics.mean(revenues)) * 100
            if margin > 15 and positive_hits > negative_hits:
                recommendation = "Buy"
            elif margin < 5 or negative_hits > positive_hits:
                recommendation = "Sell"

        insights.append(f"📌 Investment Recommendation: {recommendation}")

        return "\n".join(insights) if insights else "No meaningful financial insights extracted."

    async def _arun(self, financial_document_data: str) -> str:
        """Async version of _run."""
        return self._run(financial_document_data)

## Creating Risk Assessment Tool
class RiskTool(BaseTool, ABC):
    name: str = "Risk Assessment Tool"
    description: str = "Analyzes financial documents for risk assessment."

    async def _run(self, financial_document_data: str) -> str:
        """
        Generate a structured risk assessment from financial document data.
        """

        # === Step 1: Clean text ===
        processed_data = " ".join(financial_document_data.split())

        # === Step 2: Extract financial numbers (basic regex for debt/liabilities, assets, income) ===
        debt_matches = re.findall(r"(debt|liabilities)[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)
        asset_matches = re.findall(r"(asset[s]?)[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)
        profit_matches = re.findall(r"(net income|profit)[\w\s]*?\$?([\d,.]+)", processed_data, re.IGNORECASE)

        debts = [float(d[1].replace(",", "")) for d in debt_matches if d[1].replace(",", "").isdigit()]
        assets = [float(a[1].replace(",", "")) for a in asset_matches if a[1].replace(",", "").isdigit()]
        profits = [float(p[1].replace(",", "")) for p in profit_matches if p[1].replace(",", "").isdigit()]

        insights = []

        # === Step 3: Liquidity & Solvency risks ===
        if assets and debts:
            avg_assets = statistics.mean(assets)
            avg_debt = statistics.mean(debts)
            debt_to_assets = (avg_debt / avg_assets) if avg_assets else 0
            insights.append(f"⚖️ Debt-to-Assets Ratio: {debt_to_assets:.2f}")
            if debt_to_assets > 0.6:
                insights.append("❌ High solvency risk: Company relies heavily on debt.")
            elif debt_to_assets > 0.4:
                insights.append("⚠️ Moderate solvency risk: Debt levels may be concerning.")
            else:
                insights.append("✅ Healthy solvency position.")

        if profits and debts:
            avg_profit = statistics.mean(profits)
            avg_debt = statistics.mean(debts)
            debt_to_income = (avg_debt / avg_profit) if avg_profit else float("inf")
            insights.append(f"⚖️ Debt-to-Income Ratio: {debt_to_income:.2f}")
            if debt_to_income > 4:
                insights.append("❌ High debt servicing risk: Profits may not cover obligations.")
            elif debt_to_income > 2:
                insights.append("⚠️ Moderate debt servicing risk.")
            else:
                insights.append("✅ Debt levels manageable relative to income.")

        # === Step 4: Keyword-based qualitative risk detection ===
        market_risks = ["competition", "inflation", "recession", "regulation", "currency", "volatility"]
        operational_risks = ["lawsuit", "litigation", "supply chain", "strike", "fraud", "management failure"]
        negative_signals = ["loss", "decline", "uncertain", "risk", "default", "bankruptcy", "crisis"]

        market_hits = [word for word in market_risks if word in processed_data.lower()]
        operational_hits = [word for word in operational_risks if word in processed_data.lower()]
        negative_hits = [word for word in negative_signals if word in processed_data.lower()]

        if market_hits:
            insights.append(f"📉 Market Risks detected: {', '.join(market_hits)}")
        if operational_hits:
            insights.append(f"🏭 Operational Risks detected: {', '.join(operational_hits)}")
        if negative_hits:
            insights.append(f"⚠️ Negative Signals: {', '.join(negative_hits)}")

        # === Step 5: Overall risk rating ===
        risk_score = 0
        risk_score += 2 if any("❌" in i for i in insights) else 0
        risk_score += 1 if any("⚠️" in i for i in insights) else 0

        if risk_score >= 3:
            overall = "🔴 High Risk Investment"
        elif risk_score == 2:
            overall = "🟠 Medium Risk Investment"
        else:
            overall = "🟢 Low Risk Investment"

        insights.append(f"📌 Overall Risk Rating: {overall}")

        return "\n".join(insights) if insights else "No significant risks detected."