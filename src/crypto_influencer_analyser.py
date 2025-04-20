import random
import re
import time
from collections import Counter
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Basic web scraper to extract content from websites."""

    def __init__(self, delay=1.0):
        """Initialize the scraper.

        Args:
            delay (float): Delay between requests in seconds
        """
        self.session = requests.Session()
        self.delay = delay

        # Set a realistic user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get_page(self, url):
        """Fetch a web page.

        Args:
            url (str): The URL to fetch

        Returns:
            BeautifulSoup: Parsed HTML or None if error
        """
        try:
            # Add a random delay to avoid detection
            time.sleep(self.delay * (0.5 + random.random()))

            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None


class CoinMarketCapScraper(WebScraper):
    """Scraper to extract cryptocurrency data from CoinMarketCap."""

    def get_top_cryptocurrencies(self, limit=100):
        """Extract top cryptocurrencies from CoinMarketCap.

        Args:
            limit (int): Number of top cryptocurrencies to extract

        Returns:
            dict: Dictionary of {symbol: {name, symbol, rank}}
        """
        # CoinMarketCap shows 100 coins per page
        pages = (limit + 99) // 100
        cryptocurrencies = {}

        for page in range(1, pages + 1):
            url = f"https://coinmarketcap.com/?page={page}"
            print(f"Fetching cryptocurrencies from {url}...")

            soup = self.get_page(url)
            if not soup:
                continue

            try:
                # Extract cryptocurrency data from the page
                # The exact selector might need adjustment based on the current layout
                crypto_rows = soup.select('table tbody tr')

                for row in crypto_rows:
                    try:
                        # Extract name and symbol
                        name_element = row.select_one('.cmc-link')
                        if not name_element:
                            continue

                        name = name_element.get_text(strip=True)

                        # Extract symbol - typically near the name
                        symbol_element = row.select_one('.coin-item-symbol')
                        if symbol_element:
                            symbol = symbol_element.get_text(strip=True)
                        else:
                            # Alternative approach: try to find the symbol from the name element
                            # Often formats like "Bitcoin BTC" or "Ethereum (ETH)"
                            match = re.search(r'\(([A-Z0-9]+)\)|\s([A-Z0-9]{2,10})$', name)
                            if match:
                                symbol = match.group(1) or match.group(2)
                            else:
                                # If we can't extract the symbol, skip this cryptocurrency
                                continue

                        # Extract rank (if needed)
                        rank_element = row.select_one('.cmc-table-row td:first-child')
                        rank = int(rank_element.get_text(strip=True)) if rank_element else len(cryptocurrencies) + 1

                        # Add to our dictionary
                        cryptocurrencies[symbol] = {
                            'name': name,
                            'symbol': symbol,
                            'rank': rank
                        }

                        # Check if we've reached our limit
                        if len(cryptocurrencies) >= limit:
                            break

                    except Exception as e:
                        print(f"Error processing cryptocurrency row: {e}")
                        continue

                # Check if we've reached our limit
                if len(cryptocurrencies) >= limit:
                    break

            except Exception as e:
                print(f"Error parsing CoinMarketCap page {page}: {e}")

        # If we couldn't extract cryptocurrencies, use a fallback list
        if not cryptocurrencies:
            print("Failed to extract cryptocurrencies from CoinMarketCap. Using fallback list.")
            # Fallback list of top cryptocurrencies
            fallback_cryptos = [
                ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'Tether'), ('BNB', 'Binance Coin'),
                ('SOL', 'Solana'), ('USDC', 'USD Coin'), ('XRP', 'XRP'), ('ADA', 'Cardano'),
                ('AVAX', 'Avalanche'), ('DOGE', 'Dogecoin'), ('DOT', 'Polkadot'), ('MATIC', 'Polygon'),
                ('LINK', 'Chainlink'), ('LTC', 'Litecoin'), ('SHIB', 'Shiba Inu'), ('UNI', 'Uniswap'),
                ('TRX', 'TRON'), ('ATOM', 'Cosmos'), ('XMR', 'Monero'), ('ETC', 'Ethereum Classic'),
                ('BCH', 'Bitcoin Cash'), ('VET', 'VeChain'), ('ALGO', 'Algorand'), ('FIL', 'Filecoin'),
                ('XLM', 'Stellar'), ('MANA', 'Decentraland'), ('HBAR', 'Hedera'), ('SAND', 'The Sandbox'),
                ('NEAR', 'NEAR Protocol'), ('AXS', 'Axie Infinity'), ('FTM', 'Fantom'), ('XTZ', 'Tezos'),
                ('EGLD', 'MultiversX'), ('THETA', 'Theta Network'), ('EOS', 'EOS'), ('AAVE', 'Aave'),
                ('ZEC', 'Zcash'), ('CAKE', 'PancakeSwap'), ('ONE', 'Harmony'), ('ENJ', 'Enjin Coin')
            ]

            for i, (symbol, name) in enumerate(fallback_cryptos):
                cryptocurrencies[symbol] = {
                    'name': name,
                    'symbol': symbol,
                    'rank': i + 1
                }

        print(f"Found {len(cryptocurrencies)} cryptocurrencies.")
        return cryptocurrencies


class CryptoInfluencerScraper(WebScraper):
    """Scraper to extract crypto influencer information."""

    def extract_influencers_from_ajmarketing(self, url):
        """Extract crypto influencer handles from AJ Marketing website.

        Args:
            url (str): The URL of the AJ Marketing influencer list

        Returns:
            list: List of influencer dictionaries with name and handle
        """
        soup = self.get_page(url)
        if not soup:
            return []

        influencers = []

        # Look for Twitter handles in the page
        # This is a simplified approach - actual implementation might need adjustments
        # based on the exact structure of the page

        # Look for common patterns in the page text
        text = soup.get_text()

        # Pattern for Twitter handles: @username
        handle_pattern = r'@([A-Za-z0-9_]+)'
        handles = re.findall(handle_pattern, text)

        # Extract names near handles (simplified approach)
        for i, handle in enumerate(handles):
            # Try to find a name associated with the handle
            # For this example, we'll just use a placeholder
            name = f"Influencer {i + 1}"

            # Skip common platform mentions that might match the pattern
            if handle.lower() in ['twitter', 'instagram', 'facebook', 'youtube']:
                continue

            influencers.append({
                'name': name,
                'handle': handle
            })

        # Alternative approach: Look for sections/divs that might contain influencer info
        sections = soup.find_all(['div', 'section', 'article'])
        for section in sections:
            # Look for text that might indicate a Twitter handle
            section_text = section.get_text()
            if '@' in section_text:
                # Extract handles from this section
                section_handles = re.findall(handle_pattern, section_text)
                for handle in section_handles:
                    if handle.lower() in ['twitter', 'instagram', 'facebook', 'youtube']:
                        continue

                    # Check if this handle is already in our list
                    if not any(inf['handle'] == handle for inf in influencers):
                        influencers.append({
                            'name': f"Influencer {len(influencers) + 1}",
                            'handle': handle
                        })

        # Remove duplicates while preserving order
        unique_handles = set()
        unique_influencers = []
        for inf in influencers:
            if inf['handle'] not in unique_handles:
                unique_handles.add(inf['handle'])
                unique_influencers.append(inf)

        return unique_influencers


class CryptoTwitterAnalyser:
    """Agent that analyses crypto influencer Twitter profiles."""

    def __init__(self, crypto_data=None, delay=2.0):
        """Initialize the analyser.

        Args:
            crypto_data (dict): Dictionary of cryptocurrency data
            delay (float): Delay between requests in seconds
        """
        self.session = requests.Session()
        self.delay = delay

        # Set a realistic user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Use provided crypto data or default keywords
        if crypto_data:
            # Build crypto keywords from the provided data
            self.crypto_keywords = {}
            for symbol, data in crypto_data.items():
                # Add the symbol as a keyword
                self.crypto_keywords[symbol.lower()] = symbol

                # Add the name as a keyword
                name = data['name'].split(' ')[0]  # Use first word of name to avoid false positives
                self.crypto_keywords[name.lower()] = symbol
        else:
            # Default cryptocurrency keywords (same as in your original code)
            self.crypto_keywords = {
                'bitcoin': 'BTC',
                'btc': 'BTC',
                'ethereum': 'ETH',
                'eth': 'ETH',
                'binance': 'BNB',
                'bnb': 'BNB',
                'solana': 'SOL',
                'sol': 'SOL',
                'cardano': 'ADA',
                'ada': 'ADA',
                'ripple': 'XRP',
                'xrp': 'XRP',
                'dogecoin': 'DOGE',
                'doge': 'DOGE',
                'polkadot': 'DOT',
                'dot': 'DOT',
                'avalanche': 'AVAX',
                'avax': 'AVAX',
                'chainlink': 'LINK',
                'link': 'LINK',
                'polygon': 'MATIC',
                'matic': 'MATIC',
                'litecoin': 'LTC',
                'ltc': 'LTC',
                'stellar': 'XLM',
                'xlm': 'XLM',
                'tron': 'TRX',
                'trx': 'TRX',
                'tether': 'USDT',
                'usdt': 'USDT',
                'shiba': 'SHIB',
                'shib': 'SHIB',
                'uniswap': 'UNI',
                'uni': 'UNI',
                'near': 'NEAR',
                'monero': 'XMR',
                'xmr': 'XMR',
                'cosmos': 'ATOM',
                'atom': 'ATOM'
            }

        # Sentiment analysis keywords (unchanged)
        self.bullish_words = ['bullish', 'buy', 'long', 'hodl', 'moon', 'rally', 'undervalued',
                              'potential', 'growth', 'accumulate', 'opportunity', 'breakout', 'support',
                              'bullrun', 'uptrend', 'upside', 'profit', 'gains', 'winning', 'outperform']
        self.bearish_words = ['bearish', 'sell', 'short', 'dump', 'crash', 'drop', 'correction',
                              'overvalued', 'avoid', 'risk', 'bubble', 'resistance', 'concern',
                              'bearish', 'downtrend', 'downside', 'loss', 'losing', 'underperform']

    def analyse_twitter_profile(self, username):
        """
        Analyse a Twitter profile for cryptocurrency mentions.
        Try multiple frontend services and methods.

        Args:
            username (str): Twitter username without the @ symbol

        Returns:
            dict: Analysis results
        """
        # Add a random delay to avoid detection
        time.sleep(self.delay * (0.5 + random.random()))

        # Try multiple methods in sequence
        result = self._try_scrape_twitter_by_html(username)

        # If that failed, try alternatives
        if 'error' in result:
            # Try official search page as a last resort
            result = self._try_scrape_official_twitter(username)

        # If all methods failed, return basic profile with error
        if 'error' in result:
            return {
                'profile': {'username': username, 'name': username, 'bio': "Could not retrieve bio"},
                'analysis': {
                    'total_crypto_mentions': 0,
                    'mentioned_cryptocurrencies': {},
                    'sentiment_analysis': {},
                    'potential_recommendations': []
                },
                'tweet_count': 0,
                'tweets_analysed': [],
                'error': result['error']
            }

        return result

    def _try_scrape_twitter_by_html(self, username):
        """Try to scrape Twitter directly."""
        try:
            url = f"https://twitter.com/{username}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract profile info
            profile_info = {'username': username}

            # Twitter's structure is complex and changes often
            # This is a simplified approach that might need updates

            # Extract username from title
            title = soup.find('title')
            if title and '(' in title.text:
                profile_info['name'] = title.text.split('(')[0].strip()
            else:
                profile_info['name'] = username

            # Try to find bio
            bio_selector = soup.select('div[data-testid="UserDescription"]')
            profile_info['bio'] = bio_selector[0].text if bio_selector else "No bio available"

            # Extract tweets - this is challenging due to Twitter's dynamic loading
            tweets = []
            tweet_elements = soup.select('article[data-testid="tweet"]')

            for i, tweet_element in enumerate(tweet_elements[:20]):  # Limit to recent tweets
                tweet_text_element = tweet_element.select_one('div[data-testid="tweetText"]')
                if not tweet_text_element:
                    continue

                tweet_text = tweet_text_element.get_text(strip=True)

                # Twitter dates are complex to extract from HTML, so we'll skip for now
                tweets.append({
                    'text': tweet_text,
                    'date': ''  # Empty date
                })

                if i >= 20:  # Limit to 20 tweets
                    break

            # If we couldn't get tweets, try to at least analyse the bio
            if not tweets:
                tweets = [{'text': profile_info['bio'], 'date': ''}]

            # Analyse cryptocurrency mentions
            analysis = self.analyse_crypto_mentions(tweets, profile_info['bio'])

            return {
                'profile': profile_info,
                'analysis': analysis,
                'tweet_count': len(tweets),
                'tweets_analysed': tweets
            }

        except Exception as e:
            return {
                'username': username,
                'error': f"Error with direct Twitter scraping: {str(e)}",
                'status': getattr(e, 'response', {}).get('status_code', None) if hasattr(e, 'response') else None
            }

    def _try_scrape_official_twitter(self, username):
        """Try to scrape from official Twitter search page."""
        try:
            # Try Twitter search URL which sometimes has fewer restrictions
            search_url = f"https://twitter.com/search?q=from%3A{username}&f=live"
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract profile info - more basic info from search page
            profile_info = {'username': username, 'name': username, 'bio': "Bio not available from search page"}

            # Extract tweets from search results
            tweets = []
            tweet_elements = soup.select('article[data-testid="tweet"]')

            for i, tweet_element in enumerate(tweet_elements[:20]):
                tweet_text_element = tweet_element.select_one('div[data-testid="tweetText"]')
                if not tweet_text_element:
                    continue

                tweet_text = tweet_text_element.get_text(strip=True)

                tweets.append({
                    'text': tweet_text,
                    'date': ''  # Date not easily available
                })

                if i >= 20:  # Limit to 20 tweets
                    break

            # Analyse cryptocurrency mentions
            analysis = self.analyse_crypto_mentions(tweets, "")  # No bio from search page

            return {
                'profile': profile_info,
                'analysis': analysis,
                'tweet_count': len(tweets),
                'tweets_analysed': tweets
            }

        except Exception as e:
            return {
                'username': username,
                'error': f"Error with Twitter search scraping: {str(e)}",
                'status': getattr(e, 'response', {}).get('status_code', None) if hasattr(e, 'response') else None
            }

    def analyse_crypto_mentions(self, tweets, bio):
        """
        Analyse tweets and bio for cryptocurrency mentions.
        (This method remains unchanged from your original code)
        """
        # Combine all text for analysis
        all_text = bio + ' ' + ' '.join([t['text'] for t in tweets])
        all_text = all_text.lower()

        # Count cryptocurrency mentions
        crypto_mentions = Counter()

        for keyword, symbol in self.crypto_keywords.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            count = len(re.findall(pattern, all_text))
            if count > 0:
                crypto_mentions[symbol] += count

        # Analyse sentiment for each cryptocurrency
        sentiment_analysis = {}

        for crypto, count in crypto_mentions.most_common():
            bullish_score = 0
            bearish_score = 0

            # Look for sentiment words near cryptocurrency mentions
            for tweet in tweets:
                tweet_lower = tweet['text'].lower()

                if any(keyword.lower() in tweet_lower for keyword, symbol in self.crypto_keywords.items() if
                       symbol == crypto):
                    # Count sentiment words
                    bullish_score += sum(1 for word in self.bullish_words if word in tweet_lower)
                    bearish_score += sum(1 for word in self.bearish_words if word in tweet_lower)

            sentiment = "neutral"
            if bullish_score > bearish_score * 1.5:
                sentiment = "bullish"
            elif bearish_score > bullish_score * 1.5:
                sentiment = "bearish"

            sentiment_analysis[crypto] = {
                'mentions': count,
                'sentiment': sentiment,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score
            }

        # Find potential recommendations
        recommendations = []
        for crypto, data in sentiment_analysis.items():
            if data['sentiment'] == 'bullish' and data['mentions'] >= 2:
                recommendations.append({
                    'symbol': crypto,
                    'strength': min(10, data['bullish_score'] * data['mentions'] // 2),
                    'sentiment': data['sentiment']
                })

        # Sort recommendations by strength
        recommendations.sort(key=lambda x: x['strength'], reverse=True)

        return {
            'total_crypto_mentions': sum(crypto_mentions.values()),
            'mentioned_cryptocurrencies': dict(crypto_mentions),
            'sentiment_analysis': sentiment_analysis,
            'potential_recommendations': recommendations[:5]  # Top 5 recommendations
        }


def analyse_multiple_influencers(usernames, crypto_data=None, delay=2.0):
    """
    Analyse multiple Twitter profiles and aggregate results.

    Args:
        usernames (list): List of Twitter usernames
        crypto_data (dict): Dictionary of cryptocurrency data
        delay (float): Delay between requests

    Returns:
        dict: Aggregated analysis
    """
    analyser = CryptoTwitterAnalyser(crypto_data=crypto_data, delay=delay)

    # Collect individual analyses
    individual_analyses = []
    aggregated_mentions = Counter()
    all_recommendations = []

    for username in usernames:
        print(f"Analysing @{username}...")
        result = analyser.analyse_twitter_profile(username)

        if 'error' in result:
            print(f"Error analysing @{username}: {result['error']}")
            continue

        individual_analyses.append(result)

        # Update aggregated mentions
        for crypto, count in result['analysis']['mentioned_cryptocurrencies'].items():
            aggregated_mentions[crypto] += count

        # Collect recommendations
        for rec in result['analysis']['potential_recommendations']:
            all_recommendations.append({
                'from': username,
                'symbol': rec['symbol'],
                'strength': rec['strength'],
                'sentiment': rec['sentiment']
            })

    # Aggregate recommendations
    crypto_scores = Counter()
    crypto_mentions_by_influencers = Counter()

    for rec in all_recommendations:
        crypto_scores[rec['symbol']] += rec['strength']
        crypto_mentions_by_influencers[rec['symbol']] += 1

    # Create final recommendations list
    final_recommendations = []
    for crypto, score in crypto_scores.most_common():
        if crypto_mentions_by_influencers[crypto] > 1:  # At least 2 influencers recommend
            final_recommendations.append({
                'symbol': crypto,
                'aggregate_score': score,
                'influencer_count': crypto_mentions_by_influencers[crypto],
                'average_strength': score / crypto_mentions_by_influencers[crypto]
            })

    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'influencers_analysed': len(individual_analyses),
        'total_crypto_mentions': sum(aggregated_mentions.values()),
        'mentions_by_crypto': dict(aggregated_mentions.most_common()),
        'top_recommendations': final_recommendations[:5],  # Top 5 recommendations
        'individual_analyses': individual_analyses
    }
