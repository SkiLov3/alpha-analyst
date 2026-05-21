import yfinance as yf
import pandas as pd
import numpy as np
from tabulate import tabulate
import sys
import datetime

# EXPANDED UNIVERSE: Mixing Blue-Chip disruptors with "Mid-Cap" high-growth candidates
TICKERS = [
    # SaaS / Cloud
    "MDB", "DDOG", "NET", "SNOW", "PLTR", "OKTA", "ZS", "TEAM", "PATH",
    # Fintech / E-Commerce
    "MELI", "SE", "SHOP", "SQ", "AFRM", "SOFI", "UPST", "BILL",
    # Consumer Tech / Gaming
    "RBLX", "U", "DOCU", "S", "NFLX", "TSLA",
    # Genomics / HealthTech
    "BEAM", "EDIT", "PACB", "CRWD",
    # Big Tech Platforms
    "NVDA", "META", "AMZN", "GOOGL", "AAPL", "MSFT"
]

SECTOR_MAP = {
    "MDB": "Cloud/Data", "DDOG": "Cloud/Data", "NET": "Security/Edge", "SNOW": "Cloud/Data",
    "PLTR": "AI/Data", "OKTA": "Security/Edge", "ZS": "Security/Edge", "TEAM": "SaaS", "PATH": "AI/Automation",
    "MELI": "Fintech/Ecomm", "SE": "Fintech/Ecomm", "SHOP": "Fintech/Ecomm", "SQ": "Fintech/Ecomm",
    "AFRM": "Fintech/Ecomm", "SOFI": "Fintech/Ecomm", "UPST": "Fintech/Ecomm", "BILL": "Fintech/Ecomm",
    "RBLX": "Gaming/Metaverse", "U": "Gaming/Metaverse", "DOCU": "SaaS", "S": "Security/Edge",
    "NFLX": "Media", "TSLA": "Auto/Energy", "BEAM": "Genomics", "EDIT": "Genomics", "PACB": "Genomics",
    "CRWD": "Security/Edge", "NVDA": "Semis/AI", "META": "AdTech/Social", "AMZN": "Ecomm/Cloud",
    "GOOGL": "AdTech/Search", "AAPL": "Hardware/Services", "MSFT": "SaaS/Cloud"
}

def get_explosive_growth_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        rev_growth = info.get("revenueGrowth", 0.0)
        market_cap = info.get("marketCap", 0)
        gross_margins = info.get("grossMargins", 0.0)
        total_cash = info.get("totalCash", 0)
        total_debt = info.get("totalDebt", 1)
        cash_to_debt = total_cash / total_debt if total_debt > 0 else 5.0
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        
        # --- SCORING LOGIC ---
        growth_score = min(40, rev_growth * 100)
        
        if market_cap < 10_000_000_000:
            scale_score = 20
        elif market_cap < 50_000_000_000:
            scale_score = 15
        elif market_cap < 200_000_000_000:
            scale_score = 10
        else:
            scale_score = 5
            
        moat_score = min(20, gross_margins * 25)
        opt_score = min(20, cash_to_debt * 4)
        
        total_score = growth_score + scale_score + moat_score + opt_score
        
        return {
            "Ticker": ticker,
            "Alpha Score": round(total_score, 2),
            "Price": f"${current_price:.2f}",
            "Rev Growth": f"{rev_growth*100:.1f}%",
            "Mkt Cap": f"${market_cap/1e9:.1f}B",
            "Gross Margin": f"{gross_margins*100:.1f}%",
            "Sector": SECTOR_MAP.get(ticker, "Other"),
            "Rating": info.get("recommendationKey", "N/A").title(),
            "Thesis": "High-Velocity Disruptor" if scale_score >= 15 else "Scalable Giant"
        }
    except Exception as e:
        return None

def main():
    print(f"--- Alpha Analyst: RULE BREAKER REPORT ({datetime.date.today()}) ---")
    print("Hunting for the 'Next Netflix': High Growth, Diversified, and Scalable Platforms...")
    
    results = []
    for ticker in TICKERS:
        data = get_explosive_growth_data(ticker)
        if data:
            results.append(data)
    
    df = pd.DataFrame(results).sort_values(by="Alpha Score", ascending=False)
    
    # --- DIVERSIFICATION LOGIC ---
    # Limit to max 2 picks per sector to ensure we aren't just buying SaaS
    diversified_picks = []
    sector_counts = {}
    
    for _, row in df.iterrows():
        sector = row["Sector"]
        if sector_counts.get(sector, 0) < 2:
            diversified_picks.append(row.to_dict())
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        if len(diversified_picks) >= 10:
            break
            
    top_10 = pd.DataFrame(diversified_picks)
    top_10.insert(0, "Rank", range(1, len(top_10) + 1))
    
    cols = ["Rank", "Ticker", "Alpha Score", "Price", "Rev Growth", "Mkt Cap", "Gross Margin", "Sector", "Thesis"]
    
    print("\n--- TOP 10 DIVERSIFIED 'RULE BREAKER' PICKS ---")
    print(tabulate(top_10[cols], headers="keys", tablefmt="github", showindex=False))
    
    print("\n--- THE 'FOOLISH' INVESTMENT THESIS ---")
    print("1. Price & Momentum: Now tracking entry price alongside growth metrics.")
    print("2. Sector Diversification: Strict limits to ensure exposure across AI, Fintech, Genomics, and SaaS.")
    print("3. Rule Breaker Model: Prioritizing companies that are 'first movers' or 'disruptors' in their niche.")

if __name__ == "__main__":
    main()
