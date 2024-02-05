import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_ad_details(ad_link):
    response = requests.get(ad_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    details = {}
    description_span = soup.find('span', class_='vip-ad-description__content--wrapped')
    if description_span:
        clean_description = description_span.text.strip().replace('\r', ' ').replace('\n', ' ')
        details['description'] = clean_description
    attributes_ul = soup.find('ul', class_='vip-ad-attributes__list')
    if attributes_ul:
        for li in attributes_ul.find_all('li', class_='vip-ad-attributes__item'):
            spans = li.find_all('span')
            if len(spans) == 2:
                key = spans[0].text.strip().replace(':', '')
                value = spans[1].text.strip()
                details[key] = value
    return details

def fetch_ads_from_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} for URL: {url}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return {}
    soup = BeautifulSoup(response.text, 'html.parser')
    ads = soup.find_all('a', id=lambda x: x and x.startswith('user-ad'))
    page_ads_data = {}
    for ad in ads:
        ad_id = ad['id']
        ad_info = {
            'title': ad.find('span', class_='user-ad-row-new-design__title-span').text.strip() if ad.find('span', class_='user-ad-row-new-design__title-span') else '',
            'price': ad.find('div', class_='user-ad-price-new-design user-ad-row-new-design__price').text.strip().replace('$', '').replace('Excl. Gov. Charges', '').strip() if ad.find('div', class_='user-ad-price-new-design user-ad-row-new-design__price') else '',
            'location': ad.find('div', class_='user-ad-row-new-design__location').text.strip() if ad.find('div', class_='user-ad-row-new-design__location') else '',
            'link': urljoin(url, ad['href']) if ad.has_attr('href') else ''
        }

        attributes = ad.select('.user-ad-attributes__attribute')
        for attribute in attributes:
            attr_text = attribute.text.strip()
            if 'km' in attr_text:
                ad_info['kilometers'] = attr_text
            elif 'Ute' in attr_text or 'SUV' in attr_text or 'Sedan' in attr_text:
                ad_info['body_type'] = attr_text
            elif 'Auto' in attr_text or 'Manual' in attr_text:
                ad_info['transmission'] = attr_text
            elif 'cyl' in attr_text:
                ad_info['engine_configuration'] = attr_text

        if ad_info['link']:
            ad_details = fetch_ad_details(ad_info['link'])
            ad_info.update(ad_details)

        page_ads_data[ad_id] = ad_info
    return page_ads_data


urls = [
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/k0c18320l3008303?price=20000.00__40000.00",
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/page-2/k0c18320l3008303?price=20000.00__40000.00",
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/page-3/k0c18320l3008303?price=20000.00__40000.00",
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/page-4/k0c18320l3008303?price=20000.00__40000.00",
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/page-5/k0c18320l3008303?price=20000.00__40000.00",
        "https://www.gumtree.com.au/s-cars-vans-utes/perth/toyota+hilux/carbodytype-ute/carmake-toyota/carmodel-toyota_hilux/cartransmission-a/drivetrain-4x4/page-6/k0c18320l3008303?price=20000.00__40000.00",
        ]

# Dictionary to store all page's ads data
all_ads_data = {}

# Iterate through the URL list and crawl ads from each page
for page_url in urls:
    ads_data = fetch_ads_from_page(page_url)
    all_ads_data.update(ads_data)


import pandas as pd
import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders

df = pd.DataFrame.from_dict(all_ads_data, orient='index')

from datetime import datetime
import pytz

perth_timezone = pytz.timezone('Australia/Perth')
now_perth = datetime.now(perth_timezone)
formatted_date = now_perth.strftime("%d%b_%I:%M%p").lower()

import os
# Save data to an Excel file
excel_filename = os.path.join(os.getcwd(), 'content', f'ads_data_{formatted_date}.xlsx')
df['year'] = df['title'].str.extract(r'(\d{4})')
df['kilometers_cal'] = df['kilometers'].str.replace(' km', '').str.replace(',', '').astype(float)
df['price_cal'] = df['price'].str.replace('Negotiable', '').str.replace(',', '').astype(float)
df['km_price_rate'] = (df['kilometers_cal'] / df['price_cal']).round(2)
df['kilometers_per_year'] = df['kilometers_cal'] / (2024 - df['year'].astype(int)).round(2)
df = df.drop(['kilometers_cal', 'price_cal'], axis=1)

df.to_excel(excel_filename, index=False)
print(f"::set-output name=excel_path::{excel_filename}")