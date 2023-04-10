import json
import re
import smtplib
import ssl
import requests

from bs4 import BeautifulSoup


def scrape_elements(soup, element_type, element_class):
    return soup.find_all(element_type, class_=element_class)


def send_mail(smtp_server, sender_email, receiver_email, email_app_password, email_content):
    port = 587  # For starttls

    message = """\
    Subject: Top relevant crypto tweets from influencers

    $(user_tweets)

    This message is sent from your Personal Tweetmeister App."""

    message = message.replace("$(user_tweets)", json.dumps(email_content, indent=4))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, email_app_password)
        server.sendmail(sender_email, receiver_email, message)


def scrape_elements_from_url(url, headers, scrape_type, element_type, element_class, strip_search):
    scraped_elements = []
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, scrape_type)

    if strip_search:
        elements = soup.find_all(element_type, class_=element_class, text=re.compile(strip_search))
    else:
        elements = soup.find_all(element_type, class_=element_class)

    for element in elements:
        scraped_elements.append(element.text.strip())

    return scraped_elements

