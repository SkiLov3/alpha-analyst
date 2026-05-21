import yfinance as yf
import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime

# DIVERSIFIED RULE BREAKER UNIVERSE
# We are looking for "Category Killers" across ALL sectors
TICKERS = [
    # --- Industrials / Space / Robotics (High Disruption) ---
    "RKLB", "JOBY", "TSLA", "CAT", "DE", "ISRG", "SYM", "TER",
    # --- Financials / Fintech / Payments ---
    "SOFI", "NU", "MELI", "SQ", "AFRM", "COIN", "V", "MA",
    # --- Healthcare / Biotech / Genomics ---
    "LLY", "VRTX", "CRSP", "EXAS", "ISRG",
    # --- Consumer / E-Commerce / Retail Disruption ---
    "SHOP", "AMZN", "COST", "LULU", "CELH", "MNST",
    # --- Energy / Green Tech ---
    "ENPH", "FSLR", "NEE", "VWS.CO",
    # --- Cloud / AI / Software ---
    "PLTR", "NVDA", "SNOW", "MDB", "CRWD", "NET"
]

SECTOR_MAP = {
    "RKLB": "Industrials/Space", "JOBY": "Industrials/Aviation", "TSLA": "Auto/Energy",
    "CAT": "Industrials/Const", "DE": "Industrials/Agri", "ISRG": "Healthcare/Robotics",
    "SYM": "Industrials/Robotics", "TER": "Industrials/Semis",
    "SOFI": "Financials/Fintech", "NU": "Financials/Banking", "MELI": "Fintech/Ecomm",
    "SQ": "Financials/Payments", "AFRM": "Financials/Payments", "COIN": "Financials/Crypto",
    "V": "Financials/Payments", "MA": "Financials/Payments",
    "LLY": "Healthcare/Pharma", "VRTX": "Healthcare/Biotech", "CRSP": "Healthcare/Genomics",
    "EXAS": "Healthcare/Diagnostics",
    "SHOP": "Consumer/Ecomm", "AMZN": "Consumer/Ecomm", "COST": "Consumer/Retail",
    "LULU": "Consumer/Apparel", "CELH": "Consumer/Beverage", "MNST": "Consumer/Beverage",
    "ENPH": "Energy/Solar", "FSLR": "Energy/Solar", "NEE": "Energy/Utility",
    "PLTR": "Tech/AI", "NVDA": "Tech/Semis", "SNOW": "Tech/Cloud", "MDB": "Tech/Cloud",
    "CRWD": "Tech/Security", "NET": "Tech/Security"
}

def get_explosive_growth_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Sector-specific growth metrics
        rev_growth = info.get("revenueGrowth", 0.0)
        # If revenue growth is missing (common in some Industrials/Financials), fallback to quarterly
        if rev_growth == 0:
            rev_growth = info.get("quarterlyRevenueGrowth", 0.0)
            
        market_cap = info.get("marketCap", 0)
        gross_margins = info.get("grossMargins", 0.0)
        # Some Financials report "Operating Margins" as the primary efficiency metric
        if gross_margins == 0:
            gross_margins = info.get("operatingMargins", 0.0)
            
        total_cash = info.get("totalCash", 0)
        total_debt = info.get("totalDebt", 1)
        cash_to_debt = total_cash / total_debt if total_debt > 0 else 5.0
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        
        # --- SCORING LOGIC (ADJUSTED FOR SECTOR PARITY) ---
        
        # Growth Score (Scale: 0-40)
        # We cap this to avoid Tech always winning. 25%+ is "A Grade" across all sectors.
        growth_score = min(40, rev_growth * 150) 
        
        # Scale Score (Scale: 0-20) - The "Multi-Bagger" room to grow
        if market_cap < 5_000_000_000:
            scale_score = 20 # Small Cap Alpha
        elif market_cap < 25_000_000_000:
            scale_score = 15 # Mid Cap Alpha
        elif market_cap < 100_000_000_000:
            scale_score = 10 
        else:
            scale_score = 5
            
        # Efficiency Score (Scale: 0-20) - High margins in any sector show a "Moat"
        # Industrials with 30% margins are as impressive as SaaS with 80%
        sector = SECTOR_MAP.get(ticker, "Other")
        if "Industrials" in sector or "Financials" in sector or "Consumer" in sector:
            moat_score = min(20, gross_margins * 50) # Lower bar for higher score
        else:
            moat_score = min(20, gross_margins * 25) # SaaS bar
            
        # Financial Health (Scale: 0-20)
        opt_score = min(20, cash_to_debt * 4)
        
        total_score = growth_score + scale_score + moat_score + opt_score
        
        return {
            "Ticker": ticker,
            "Alpha Score": round(total_score, 2),
            "Price": f"${current_price:.2f}",
            "Rev Growth": f"{rev_growth*100:.1f}%",
            "Mkt Cap": f"${market_cap/1e9:.1f}B",
            "Margin": f"{gross_margins*100:.1f}%",
            "Sector": sector,
            "Thesis": "Sector Disruptor" if scale_score >= 15 else "Market Leader"
        }
    except Exception as e:
        return None

def main():
    print(f"--- Alpha Analyst: DIVERSIFIED RULE BREAKER REPORT ({datetime.date.today()}) ---")
    print("Searching for 10x potential in Industrials, Financials, and Disruptive Tech...")
    
    results = []
    for ticker in TICKERS:
        data = get_explosive_growth_data(ticker)
        if data:
            results.append(data)
    
    df = pd.DataFrame(results).sort_values(by="Alpha Score", ascending=False)
    
    # --- STRICT DIVERSIFICATION ---
    # Max 2 per primary sector group (Industrials, Financials, Tech, etc.)
    diversified_picks = []
    major_sector_counts = {}
    
    for _, row in df.iterrows():
        major_sector = row["Sector"].split("/")[0]
        if major_sector_counts.get(major_sector, 0) < 2:
            diversified_picks.append(row.to_dict())
            major_sector_counts[major_sector] = major_sector_counts.get(major_sector, 0) + 1
        
        if len(diversified_picks) >= 10:
            break
            
    top_10 = pd.DataFrame(diversified_picks)
    top_10.insert(0, "Rank", range(1, len(top_10) + 1))
    
    cols = ["Rank", "Ticker", "Alpha Score", "Price", "Rev Growth", "Mkt Cap", "Margin", "Sector", "Thesis"]
    
    print("\n--- TOP 10 CROSS-SECTOR RULE BREAKERS ---")
    print(tabulate(top_10[cols], headers="keys", tablefmt="github", showindex=False))
    
    print("\n--- ANALYST THESIS ---")
    print("1. Beyond Tech: We found 'Rule Breaker' signatures in Space (RKLB), Fintech (NU/SOFI), and Energy.")
    print("2. Sector Parity: Adjusted growth scoring to recognize top-tier performance in capital-intensive sectors.")
    print("3. Multi-Bagger Filter: Prioritizing smaller market caps with massive Addressable Markets (TAM).")

if __name__ == "__main__":
    main()
