import yfinance as yf
import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime

# Institutional Universe: Top S&P 500 components across sectors
# In a production setting, this would fetch the full S&P 500 list
TICKERS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "NVDA", "AVGO", "ORCL",
    # Healthcare
    "UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO",
    # Financials
    "JPM", "V", "MA", "BAC", "MS", "GS",
    # Consumer Disc
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX",
    # Consumer Staples
    "PG", "KO", "PEP", "COST", "WMT",
    # Energy
    "XOM", "CVX", "SLB",
    # Industrials
    "CAT", "GE", "UNP", "HON",
    # Communication
    "META", "NFLX", "DIS",
]

SECTORS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "AVGO", "ORCL"],
    "Healthcare": ["UNH", "LLY", "JNJ", "ABBV", "MRK", "TMO"],
    "Financials": ["JPM", "V", "MA", "BAC", "MS", "GS"],
    "Consumer": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "PG", "KO", "PEP", "COST", "WMT"],
    "Industrials/Energy": ["XOM", "CVX", "SLB", "CAT", "GE", "UNP", "HON"],
    "Media/Comm": ["META", "NFLX", "DIS"]
}

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Scoring Factors (Medium/Long Term Focus)
        # 1. PEG Ratio (Growth at Reasonable Price) - Lower is better
        peg = info.get("pegRatio", 2.0)
        
        # 2. ROE (Efficiency) - Higher is better
        roe = info.get("returnOnEquity", 0.0)
        
        # 3. Debt/Equity (Solvency) - Lower is better
        debt_to_equity = info.get("debtToEquity", 100.0) / 100.0
        
        # 4. Profit Margins
        margins = info.get("profitMargins", 0.0)
        
        # 5. Distance from 200DMA (Trend)
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        dma_200 = info.get("twoHundredDayAverage", current_price)
        trend = (current_price - dma_200) / dma_200 if dma_200 else 0
        
        # Normalized Scores (0-10)
        # PEG: < 1 is perfect (10), > 3 is poor (0)
        peg_score = max(0, min(10, (3 - peg) * 5))
        
        # ROE: > 20% is perfect (10), < 5% is poor (0)
        roe_score = max(0, min(10, roe * 50))
        
        # Debt: < 0.2 is perfect (10), > 1.5 is poor (0)
        debt_score = max(0, min(10, (1.5 - debt_to_equity) * 7))
        
        # Trend: Positive trend but not overextended (Ideally 5-15% above 200DMA)
        if 0.05 < trend < 0.20:
            trend_score = 10
        elif trend > 0.20:
            trend_score = 7 # Overextended
        elif trend > 0:
            trend_score = 5 # Weak trend
        else:
            trend_score = 2 # Downtrend
            
        total_score = (peg_score * 0.4) + (roe_score * 0.3) + (debt_score * 0.2) + (trend_score * 0.1)
        
        return {
            "Ticker": ticker,
            "Score": round(total_score, 2),
            "Price": current_price,
            "PEG": peg,
            "ROE": f"{roe*100:.1f}%",
            "D/E": round(debt_to_equity, 2),
            "Trend": f"{trend*100:+.1f}% vs 200DMA",
            "Sector": next((s for s, tks in SECTORS.items() if ticker in tks), "Other")
        }
    except Exception as e:
        return None

def main():
    print(f"--- Alpha Analyst Morning Report: {datetime.date.today()} ---")
    print("Analyzing institutional universe for High-Conviction Medium-Term plays...")
    
    results = []
    for ticker in TICKERS:
        data = get_stock_data(ticker)
        if data:
            results.append(data)
    
    df = pd.DataFrame(results)
    
    # Diversification Logic: Pick Top 2 from each sector, then fill remaining
    top_picks = []
    for sector in SECTORS.keys():
        sector_stocks = df[df["Sector"] == sector].sort_values(by="Score", ascending=False).head(2)
        top_picks.extend(sector_stocks.to_dict("records"))
    
    # Fill up to 10 if needed (or trim if we have more than 10)
    top_picks_df = pd.DataFrame(top_picks).sort_values(by="Score", ascending=False).head(10)
    
    print("\n--- TOP 10 INSTITUTIONAL PICKS (DIVERSIFIED) ---")
    print(tabulate(top_picks_df, headers="keys", tablefmt="github", showindex=False))
    
    print("\n--- ANALYST THESIS ---")
    print("1. Strategy: Quality at a Reasonable Price (QARP).")
    print("2. Horizon: 6-12 Months (Medium-Long Term).")
    print("3. Selection: Filters for high ROE, manageable debt, and positive growth trajectory.")

if __name__ == "__main__":
    main()
