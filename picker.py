import yfinance as yf
import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime

# Institutional Universe: Top S&P 500 components across sectors
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
        
        # 1. PEG Ratio (Growth at Reasonable Price) - Lower is better
        peg = info.get("pegRatio", 2.0)
        
        # 2. ROE (Efficiency) - Higher is better
        roe = info.get("returnOnEquity", 0.0)
        
        # 3. Debt/Equity (Solvency) - Lower is better
        debt_to_equity = info.get("debtToEquity", 100.0) / 100.0
        
        # 4. Analyst Ratings (Consensus)
        # recommendationMean: 1.0 (Strong Buy) to 5.0 (Strong Sell)
        rating_mean = info.get("recommendationMean", 3.0) 
        rating_key = info.get("recommendationKey", "hold").replace("_", " ").title()
        
        # 5. Distance from 200DMA (Trend)
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        dma_200 = info.get("twoHundredDayAverage", current_price)
        trend = (current_price - dma_200) / dma_200 if dma_200 else 0
        
        # --- Normalized Scores (0-10) ---
        # PEG: < 1 is perfect (10), > 3 is poor (0)
        peg_score = max(0, min(10, (3 - peg) * 5))
        
        # ROE: > 20% is perfect (10), < 5% is poor (0)
        roe_score = max(0, min(10, roe * 50))
        
        # Debt: < 0.2 is perfect (10), > 1.5 is poor (0)
        debt_score = max(0, min(10, (1.5 - debt_to_equity) * 7))
        
        # Analyst: 1.0 -> 10, 3.0 -> 5, 5.0 -> 0
        analyst_score = max(0, min(10, (5 - rating_mean) * 2.5))
        
        # Trend: Positive trend but not overextended
        if 0.05 < trend < 0.20:
            trend_score = 10
        elif trend > 0.20:
            trend_score = 7 
        elif trend > 0:
            trend_score = 5 
        else:
            trend_score = 2 
            
        # Weighted Total Score
        total_score = (
            (peg_score * 0.35) + 
            (roe_score * 0.25) + 
            (debt_score * 0.15) + 
            (analyst_score * 0.15) + 
            (trend_score * 0.10)
        )
        
        return {
            "Ticker": ticker,
            "Score": round(total_score, 2),
            "Price": current_price,
            "Rating": f"{rating_key} ({rating_mean})",
            "PEG": peg,
            "ROE": f"{roe*100:.1f}%",
            "D/E": round(debt_to_equity, 2),
            "Trend": f"{trend*100:+.1f}%",
            "Sector": next((s for s, tks in SECTORS.items() if ticker in tks), "Other")
        }
    except Exception as e:
        return None

def main():
    print(f"--- Alpha Analyst Morning Report: {datetime.date.today()} ---")
    print("Synthesizing Fundamental, Technical, and Analyst Consensus data...")
    
    results = []
    for ticker in TICKERS:
        data = get_stock_data(ticker)
        if data:
            results.append(data)
    
    df = pd.DataFrame(results)
    
    # Global Ranking
    df = df.sort_values(by="Score", ascending=False)
    df.insert(0, "Rank", range(1, len(df) + 1))
    
    # Diversification Selection (Top from each sector)
    top_picks = []
    for sector in SECTORS.keys():
        sector_stocks = df[df["Sector"] == sector].head(2)
        top_picks.extend(sector_stocks.to_dict("records"))
    
    # Final Top 10 Diversified
    top_picks_df = pd.DataFrame(top_picks).sort_values(by="Score", ascending=False).head(10)
    # Recalculate rank display for the final 10
    top_picks_df["Display Rank"] = range(1, 11)
    
    cols = ["Display Rank", "Ticker", "Score", "Rating", "Price", "PEG", "ROE", "Trend", "Sector"]
    
    print("\n--- TOP 10 INSTITUTIONAL PICKS (RANKED & DIVERSIFIED) ---")
    print(tabulate(top_picks_df[cols], headers="keys", tablefmt="github", showindex=False))
    
    print("\n--- ANALYST THESIS ---")
    print("1. Ranking: Quantitative blend of growth, efficiency, and wall street sentiment.")
    print("2. Consensus: Integrated mean ratings from major investment banks.")
    print("3. Selection: Diversified across sectors to minimize idiosyncratic risk.")

if __name__ == "__main__":
    main()
