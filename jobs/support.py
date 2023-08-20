from utils import *
import bs4
import re

# https://regex101.com/r/xqKBPL/1
REGEX_SUPPORT_MIN_NUMBER = re.compile('([1-9][0-9\.,]+(?: ?[0-9]+)?)')

def get_support_prices():
    prices = {
        'premium': {'percent': 0, 'minimum': None},
        'business': {'percent': 10, 'minimum': None},
        'entreprise': {'percent': 30, 'minimum': None},
    }
    subs = {}
    for sub in SUBSIDIARIES:
        for s in get_website_tries_for_country(sub):
            try:
                html = get_html(f'https://www.ovhcloud.com/{s.lower()}/support-levels/plans/')
                soup = bs4.BeautifulSoup(html, 'lxml')
                th = soup.css.select('table thead tr:nth-child(3) th')
                if not bool(th) or len(th) < 5:
                    continue
                i = 2
                for key in dict.keys(prices):
                    m0 = re.findall(REGEX_SUPPORT_MIN_NUMBER, th[i].get_text().replace(u"\u00A0", " "))
                    if bool(m0):
                        prices[key]['minimum'] = float(m0[0].replace(' ', '').replace(',', '.'))
                    i += 1
                break
            except urllib.error.HTTPError: # 404 not found
                pass
        subs[sub] = prices
    return subs


if __name__ == '__main__':
    get_support_prices()