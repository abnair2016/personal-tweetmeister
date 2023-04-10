import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


def mockenv(**envvars):
    return patch.dict(os.environ, envvars)


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture()
def test_client():
    return TestClient(app)


@patch('main.scrape_elements_from_url', new_callable=MagicMock)
def test_scrape_elements_from_page(mock_scrape_elements_from_url, test_client):
    expected_result = ["element1", "element2"]

    # Configure the mock
    mock_scrape_elements_from_url.return_value = expected_result

    # Prepare the request
    url = "https://example.com"
    headers = {"header1": "value1"}
    scrape_type = "html.parser"
    element_type = "div"
    element_class = "example"
    strip_search = "regex"

    # Make the request
    response = test_client.post("/scrape", json={
        "url": url,
        "headers": headers,
        "scrape_type": scrape_type,
        "element_type": element_type,
        "element_class": element_class,
        "strip_search": strip_search
    })

    # Check the response
    assert response.status_code == 200
    assert response.json() == expected_result

    # Check the mock was called with the right arguments
    mock_scrape_elements_from_url.assert_called_once_with(
        url=url,
        headers=headers,
        scrape_type=scrape_type,
        element_type=element_type,
        element_class=element_class,
        strip_search=strip_search
    )


@patch('main.scrape_elements_from_url', new_callable=MagicMock)
@patch('main.sntwitter.TwitterSearchScraper', new_callable=MagicMock)
def test_scrape_crypto_tweets(mock_twitter_scraper, mock_scrape_elements_from_url, test_client):
    expected_result = {'test_handle': [{'content': 'tweet btc content',
                                        'id': 0,
                                        'likes': 10,
                                        'source': 'Twitter',
                                        'when': str(datetime.now().date())}]}

    # Configure the mocks
    mock_twitter_scraper.return_value.get_items.return_value = [
        MagicMock(date=datetime.now(),
                  likeCount=10,
                  sourceLabel="Twitter",
                  rawContent="tweet btc content")
    ]
    mock_scrape_elements_from_url.side_effect = ["btc", "eth"], ["Bitcoin", "Ethereum"]

    # Prepare the request
    handle = "test_handle"

    # Make the request
    response = test_client.get(f"/crypto/tweets/handle/{handle}")

    # Check the response
    assert response.status_code == 200
    assert response.json() == expected_result

    # Check the mocks were called with the right arguments
    mock_scrape_elements_from_url.count(2)
    mock_twitter_scraper.assert_called_once_with(f"from:{handle}")


@patch('main.scrape_elements_from_url', new_callable=MagicMock)
@patch('main.scrape_crypto_tweets', new_callable=AsyncMock)
@patch('main.check_and_send_mail', new_callable=AsyncMock)
@mockenv(
    EMAIL_SMTP="smtp.testmail.com",
    RECEIVER_EMAIL="receiver@testmail.com",
    SENDER_EMAIL="sender@testmail.com",
    EMAIL_PWD="password"
)
def test_scrape_crypto_tweets_from_influencers(mock_check_and_send_mail, mock_scrape_crypto_tweets,
                                               mock_scrape_elements_from_url, test_client):
    expected_result = {
        'influencer1': [
            {'id': 0, 'when': '2023-04-08', 'likes': 10, 'source': 'Twitter', 'content': 'tweet btc content'}],
        'influencer2': [
            {'id': 50, 'when': '2023-04-08', 'likes': 1, 'source': 'Twitter', 'content': 'tweet eth content'}]
    }

    mock_scrape_elements_from_url.return_value = ["influencer1", "influencer2"]
    mock_scrape_crypto_tweets.side_effect = [
        {"influencer1": [
            {"id": 0, "when": "2023-04-08", "likes": 10, "source": "Twitter", "content": "tweet btc content"}]},
        {"influencer2": [
            {"id": 50, "when": "2023-04-08", "likes": 1, "source": "Twitter", "content": "tweet eth content"}]}
    ]

    response = test_client.get("/crypto/tweets/influencers")

    assert response.status_code == 200
    assert response.json() == expected_result
    data = json.loads(response.content)
    for handle in data:
        assert isinstance(data[handle], list)
        assert all(isinstance(tweet, dict) for tweet in data[handle])
        assert all(
            key in tweet for tweet in data[handle] for key in ["id", "when", "likes", "source", "content"]
        )

    assert mock_check_and_send_mail.called is True
    assert mock_check_and_send_mail.call_count == 1
    mock_check_and_send_mail.assert_called_once_with(
        'smtp.testmail.com',
        'sender@testmail.com',
        'receiver@testmail.com',
        'password',
        {
            'influencer1': [
                {'id': 0, 'when': '2023-04-08', 'likes': 10, 'source': 'Twitter', 'content': 'tweet btc content'}
            ],
            'influencer2': [
                {'id': 50, 'when': '2023-04-08', 'likes': 1, 'source': 'Twitter', 'content': 'tweet eth content'}
            ]
        }
    )
