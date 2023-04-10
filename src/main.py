import datetime
import os

import snscrape.modules.twitter as sntwitter
import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from models import UserTweet, ScrapeElement
from utils import send_mail, scrape_elements_from_url

# Defaults
TOP_100_CRYPTO_URL = "https://coinmarketcap.com"
HTML_PARSER = "html.parser"
CRYPTO_ELEMENT_TYPE = "p"
CRYPTO_SYMBOLS_CLASS = "sc-4984dd93-0 iqdbQL coin-item-symbol"
CRYPTO_NAMES_CLASS = "sc-4984dd93-0 kKpPOn"
TOP_CRYPTO_INFLUENCER_URL = "https://www.ajmarketing.io/post/top-31-crypto-twitter-influencers-by-followers-in-2022"
INFLUENCER_TYPE = "u"
INFLUENCER_CLASS = "_3zM-5"
STRIP_SEARCH_REGEX = "^@"


app = FastAPI()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.post("/scrape")
async def scrape_elements_from_page(scrape_element: ScrapeElement):
    """
    Scrapes a given html page with any element type and class into a list.

    Request Body:

        url (string): The url of the html page that is to be scraped

        headers (dict, optional): The headers to be sent to scrape the url (if any)

        scrape_type (string): The type of scraping required. Example: `html.parser` or `lxml`

        element_type (string): The type of html element to scrape from.
        Example: `p`, `u`, `h1`, `a`, `span`, `div`, etc.

        element_class (string): CSS class used to style the html element

        strip_search (string): Regex of any text format to strip out from the resultant text in list

    Returns:

        List of elements from the scraped page
    """
    return scrape_elements_from_url(
        url=scrape_element.url,
        headers=scrape_element.headers,
        scrape_type=scrape_element.scrape_type,
        element_type=scrape_element.element_type,
        element_class=scrape_element.element_class,
        strip_search=scrape_element.strip_search
    )


@app.get("/crypto/tweets/handle/{handle}")
async def scrape_crypto_tweets(handle):
    """
    Scrapes tweets about any of the top cryptocurrencies tweeted by a given Twitter user's handle today

    Path Params:

        handle (string): The Twitter user's handle who may have tweeted about any of the top cryptocurrencies today

    Returns:

        List of relevant top cryptocurrency tweets today scraped from the provided Twitter user handle
    """
    crypto_url = os.getenv('CRYPTO_URL', TOP_100_CRYPTO_URL)
    crypto_page_type = os.getenv('CRYPTO_PAGE_TYPE', HTML_PARSER)
    crypto_element_type = os.getenv('CRYPTO_ELEMENT_TYPE', CRYPTO_ELEMENT_TYPE)
    crypto_symbols_element_class = os.getenv('CRYPTO_SYMBOLS_ELEMENT_CLASS', CRYPTO_SYMBOLS_CLASS)
    crypto_names_element_class = os.getenv('CRYPTO_NAMES_ELEMENT_CLASS', CRYPTO_NAMES_CLASS)

    cryptos_symbols = scrape_elements_from_url(
        url=crypto_url,
        headers=None,
        scrape_type=crypto_page_type,
        element_type=crypto_element_type,
        element_class=crypto_symbols_element_class,
        strip_search=None
    )

    cryptos_names = scrape_elements_from_url(
        url=crypto_url,
        headers=None,
        scrape_type=crypto_page_type,
        element_type=crypto_element_type,
        element_class=crypto_names_element_class,
        strip_search=None
    )

    cryptos = cryptos_symbols + cryptos_names

    # Created a list to append all user tweets
    user_tweets: list[UserTweet] = []
    # Using TwitterSearchScraper to scrape data and append user tweets to list
    for tweet_count, tweet in enumerate(sntwitter.TwitterSearchScraper('from:' + handle).get_items()):
        user_tweet = UserTweet(
            id=tweet_count,
            when=str(tweet.date.date()),
            likes=tweet.likeCount,
            source=tweet.sourceLabel,
            content=tweet.rawContent.encode('utf-8')
        )

        if tweet.date.date() < datetime.datetime.today().date():
            break

        for crypto in cryptos:
            if crypto.lower() in user_tweet.content.lower().split() or \
                    "#" + crypto.lower() in user_tweet.content.lower().split():
                user_tweets.append(user_tweet)

    user_tweets_by_handle = {handle: jsonable_encoder(user_tweets)}

    return user_tweets_by_handle


@app.get("/crypto/tweets/influencers")
async def scrape_crypto_tweets_from_influencers():
    """
    Scrapes tweets about any of the top cryptocurrencies tweeted by a defined list of
    Top trending Cryptocurrency Influencer's Twitter handle today

    Returns:

        List of relevant top cryptocurrency tweets today scraped from all
        top trending cryptocurrency influencers' Twitter handles
    """
    influencer_url = os.getenv('INFLUENCER_URL', TOP_CRYPTO_INFLUENCER_URL)
    influencer_page_type = os.getenv('INFLUENCER_PAGE_TYPE', HTML_PARSER)
    influencer_element_type = os.getenv('INFLUENCER_ELEMENT_TYPE', INFLUENCER_TYPE)
    influencer_element_class = os.getenv('INFLUENCER_ELEMENT_CLASS', INFLUENCER_CLASS)
    strip_search_regex = os.getenv('STRIP_SEARCH_REGEX', STRIP_SEARCH_REGEX)
    smtp_server = os.getenv('EMAIL_SMTP', None)
    receiver_email = os.getenv('RECEIVER_EMAIL', None)
    sender_email = os.getenv('SENDER_EMAIL', None)
    email_app_password = os.getenv('EMAIL_PWD', None)

    crypto_influencers = scrape_elements_from_url(
        url=influencer_url,
        headers=None,
        scrape_type=influencer_page_type,
        element_type=influencer_element_type,
        element_class=influencer_element_class,
        strip_search=strip_search_regex
    )

    all_influencers_tweets = {}
    for influencer_handle in crypto_influencers:
        print(influencer_handle)
        all_influencers_tweets.update(await scrape_crypto_tweets(influencer_handle))

    push_mail = False
    email_values_exist = smtp_server and receiver_email and sender_email and email_app_password
    print(email_values_exist)
    for tweet in all_influencers_tweets:
        if len(all_influencers_tweets[tweet]) > 0 and email_values_exist:
            push_mail = True
            break
        else:
            push_mail = False

    if push_mail:
        print(f"Emailing relevant tweets from today from "
              f"top trending crypto influencers about top cryptos: {crypto_influencers}")
        await check_and_send_mail(smtp_server, sender_email, receiver_email, email_app_password, all_influencers_tweets)

    return all_influencers_tweets


async def check_and_send_mail(smtp_server, sender, receiver, app_password, content):
    send_mail(
        smtp_server=smtp_server,
        sender_email=sender,
        receiver_email=receiver,
        email_app_password=app_password,
        email_content=content
    )
