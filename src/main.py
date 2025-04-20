from fastapi import FastAPI, Query
from typing import List, Optional
from crypto_influencer_analyser import (
    CoinMarketCapScraper,
    CryptoInfluencerScraper,
    CryptoTwitterAnalyser,
    analyse_multiple_influencers,
)

app = FastAPI(
    title="Crypto Influencer Analyser API",
    description="Analyse crypto Twitter influencers for sentiment and recommendations",
    version="1.0.0"
)


@app.get("/top-cryptos")
def get_top_cryptocurrencies(limit: int = 100):
    scraper = CoinMarketCapScraper()
    return scraper.get_top_cryptocurrencies(limit=limit)


@app.get("/influencers")
def get_influencers(
    url: str = "https://www.ajmarketing.io/post/top-31-crypto-twitter-influencers-by-followers-in-2022"
):
    scraper = CryptoInfluencerScraper()
    return scraper.extract_influencers_from_ajmarketing(url)


@app.get("/analyse/{username}")
def analyse_influencer(username: str):
    analyser = CryptoTwitterAnalyser()
    return analyser.analyse_twitter_profile(username)


@app.post("/analyse-multiple")
def analyse_multiple(usernames: List[str] = Query(...), delay: Optional[float] = 2.0):
    return analyse_multiple_influencers(usernames, delay=delay)
