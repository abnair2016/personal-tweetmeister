from unittest.mock import patch, MagicMock

from crypto_influencer_analyser import (
    CoinMarketCapScraper,
    CryptoInfluencerScraper,
    CryptoTwitterAnalyser,
    analyse_multiple_influencers,
)


def test_coinmarketcap_scraper_fallback(monkeypatch):
    """Test fallback path for CoinMarketCap scraper when no HTML is returned."""

    scraper = CoinMarketCapScraper()

    # Simulate `get_page` always returning None (e.g., request failure)
    monkeypatch.setattr(scraper, 'get_page', lambda url: None)

    cryptos = scraper.get_top_cryptocurrencies(limit=5)
    assert isinstance(cryptos, dict)
    assert 'BTC' in cryptos  # Fallback includes BTC
    assert len(cryptos) >= 5


def test_influencer_scraper_handles(monkeypatch):
    """
    Test influencer scraping with mocked HTML containing @handles.
    html = "<html><body><p>@testuser1 @elonmusk @facebook</p></body></html>"
    """

    mock_soup = MagicMock()
    mock_soup.get_text.return_value = "@testuser1 @elonmusk @facebook"
    mock_soup.find_all.return_value = []

    scraper = CryptoInfluencerScraper()
    monkeypatch.setattr(scraper, 'get_page', lambda url: mock_soup)

    influencers = scraper.extract_influencers_from_ajmarketing("http://fakeurl.com")
    handles = [inf["handle"] for inf in influencers]

    assert "testuser1" in handles
    assert "elonmusk" in handles
    assert "facebook" not in handles  # filtered out


def test_analyse_mentions_basic():
    """Test sentiment and crypto mention extraction logic."""
    tweets = [
        {"text": "Bitcoin and Ethereum to the moon! Very bullish outlook.", "date": ""},
        {"text": "Avoid DOGE, looks like a dump incoming.", "date": ""}
    ]
    bio = "Crypto fan. HODLing BTC, ETH, DOGE."

    analyser = CryptoTwitterAnalyser()
    results = analyser.analyse_crypto_mentions(tweets, bio)

    assert results["total_crypto_mentions"] >= 3
    assert results["sentiment_analysis"]["BTC"]["sentiment"] == "bullish"
    assert results["sentiment_analysis"]["DOGE"]["sentiment"] == "bearish"


@patch("crypto_influencer_analyser.CryptoTwitterAnalyser.analyse_twitter_profile")
def test_analyse_multiple_influencers(mock_analyse):
    """Test aggregation logic from multiple influencers."""

    mock_analyse.side_effect = [
        {
            "profile": {"username": "user1", "bio": "", "name": "User One"},
            "analysis": {
                "total_crypto_mentions": 2,
                "mentioned_cryptocurrencies": {"BTC": 1, "ETH": 1},
                "sentiment_analysis": {
                    "BTC": {"mentions": 1, "sentiment": "bullish", "bullish_score": 3, "bearish_score": 0},
                    "ETH": {"mentions": 1, "sentiment": "bullish", "bullish_score": 2, "bearish_score": 0},
                },
                "potential_recommendations": [
                    {"symbol": "BTC", "strength": 5, "sentiment": "bullish"}
                ],
            },
            "tweet_count": 2,
            "tweets_analysed": [],
        },
        {
            "profile": {"username": "user2", "bio": "", "name": "User Two"},
            "analysis": {
                "total_crypto_mentions": 1,
                "mentioned_cryptocurrencies": {"BTC": 1},
                "sentiment_analysis": {
                    "BTC": {"mentions": 1, "sentiment": "bullish", "bullish_score": 3, "bearish_score": 0}
                },
                "potential_recommendations": [
                    {"symbol": "BTC", "strength": 5, "sentiment": "bullish"}
                ],
            },
            "tweet_count": 2,
            "tweets_analysed": [],
        }
    ]

    results = analyse_multiple_influencers(["user1", "user2"])

    assert results["influencers_analysed"] == 2
    assert "BTC" in results["mentions_by_crypto"]
    assert results["top_recommendations"][0]["symbol"] == "BTC"
    assert results["top_recommendations"][0]["influencer_count"] == 2
