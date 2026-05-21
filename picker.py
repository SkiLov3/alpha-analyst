import yfinance as yf
import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime

# EXPANDED UNIVERSE: Mixing Blue-Chip disruptors with "Mid-Cap" high-growth candidates
# This is where we look for the "Next Netflix" or "Next Tesla"
TICKERS = [
    # The "Rule Breakers" / High Growth Mid-Caps
    "MDB", "DDOG", "NET", "SNOW", "PLTR", "CRWD", "MELI", "SE", "SHOP", "SQ",
    "U", "RBLX", "OKTA", "ZS", "TEAM", "DOCU", "BILL", "PATH", "S", "GNS",
    # Emerging Tech / Genomics / Fintech
    "BEAM", "EDIT", "PACB", "AFRM", "SOFI", "UPST",
    # Scalable Platforms (The "Obvious" ones that still have long runways)
    "NVDA", "TSLA", "NFLX", "META", "AMZN", "GOOGL", "AAPL", "MSFT"
]

def get_explosive_growth_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # --- MOTLEY FOOL / RULE BREAKER METRICS ---
        
        # 1. Revenue Growth (The Engine) - We want > 20% consistently
        rev_growth = info.get("revenueGrowth", 0.0)
        
        # 2. Market Cap (The "Room to Grow") 
        # A $3T company (AAPL) rarely 10xs. A $10B company (MDB) can.
        market_cap = info.get("marketCap", 0)
        
        # 3. Gross Margins (Pricing Power / Scalability)
        # Software-like margins (>70%) are the holy grail of multi-baggers.
        gross_margins = info.get("grossMargins", 0.0)
        
        # 4. Cash Position vs Debt (Optionality)
        total_cash = info.get("totalCash", 0)
        total_debt = info.get("totalDebt", 1)
        cash_to_debt = total_cash / total_debt if total_debt > 0 else 5.0
        
        # 5. Volatility / Beta (Fool strategy embraces volatility)
        beta = info.get("beta", 1.0)
        
        # --- SCORING LOGIC ---
        
        # Growth Score: 0-40 points. (30%+ growth is the sweet spot)
        growth_score = min(40, rev_growth * 100)
        
        # Scale Score: 0-20 points. (Smaller is better for 10x potential)
        # < $10B = 20 pts, $10B-$50B = 15 pts, $50B-$200B = 10 pts, > $500B = 5 pts
        if market_cap < 10_000_000_000:
            scale_score = 20
        elif market_cap < 50_000_000_000:
            scale_score = 15
        elif market_cap < 200_000_000_000:
            scale_score = 10
        else:
            scale_score = 5
            
        # Profitability/Moat Score: 0-20 points. (High gross margins indicate a moat)
        moat_score = min(20, gross_margins * 25)
        
        # Optionality Score: 0-20 points. (Cash to burn for R&D/Acquisitions)
        opt_score = min(20, cash_to_debt * 4)
        
        total_score = growth_score + scale_score + moat_score + opt_score
        
        return {
            "Ticker": ticker,
            "Alpha Score": round(total_score, 2),
            "Rev Growth": f"{rev_growth*100:.1f}%",
            "Mkt Cap": f"${market_cap/1e9:.1f}B",
            "Gross Margin": f"{gross_margins*100:.1f}%",
            "Price": info.get("currentPrice", 0),
            "Rating": info.get("recommendationKey", "N/A").title(),
            "Thesis": "High-Velocity Disruptor" if scale_score >= 15 else "Scalable Giant"
        }
    except Exception as e:
        return None

def main():
    print(f"--- Alpha Analyst: RULE BREAKER REPORT ({datetime.date.today()}) ---")
    print("Hunting for the 'Next Netflix': High Growth, High Margin, Scalable Platforms...")
    
    results = []
    for ticker in TICKERS:
        data = get_explosive_growth_data(ticker)
        if data:
            results.append(data)
    
    df = pd.DataFrame(results).sort_values(by="Alpha Score", ascending=False)
    
    # Select Top 10 by Alpha Score (Potential Multi-Baggers)
    top_10 = df.head(10).copy()
    top_10.insert(0, "Rank", range(1, 11))
    
    cols = ["Rank", "Ticker", "Alpha Score", "Rev Growth", "Mkt Cap", "Gross Margin", "Rating", "Thesis"]
    
    print("\n--- TOP 10 'RULE BREAKER' PICKS (EXPLOSIVE POTENTIAL) ---")
    print(tabulate(top_10[cols], headers="keys", tablefmt="github", showindex=False))
    
    print("\n--- THE 'FOOLISH' INVESTMENT THESIS ---")
    print("1. Revenue Growth is King: We prioritize top-line acceleration over current PE ratios.")
    print("2. Market Cap Ceiling: Smaller companies have much higher 'Alpha' potential (The 10x Factor).")
    print("3. Moats & Margins: High gross margins prove the company has an unfair advantage in its niche.")
    print("4. Volatility is an Opportunity: These stocks will swing wildly. Hold for 3-5+ years.")

if __name__ == "__main__":
    main()
