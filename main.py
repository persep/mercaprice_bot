import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from io import StringIO
import os
import matplotlib.dates as mdates
from fastapi import Request, FastAPI
import matplotlib.ticker as mticker
import numpy as np

months=['', 'ene', 'feb', 'mar', 'abr', 'may', 'jun',
        'jul', 'ago', 'sept', 'oct', 'nov', 'dic']

app = FastAPI()

def start_client():
    api_key = os.getenv('api_key')
    api_key_secret = os.getenv('api_key_secret')
    access_token = os.getenv('access_token')
    access_token_secret = os.getenv('access_token_secret')
    bearer_token = os.getenv('bearer_token')

    auth = tweepy.OAuth1UserHandler(
        api_key, api_key_secret, access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    return client, api

def mydate(date, fmt):
    if fmt == 'MMM':
        return months[date.month]
    if fmt == 'MMM-yyyy':
        return f'{months[date.month]}-{date.year}'
    if fmt == 'yyyy':
        return date.year
    if fmt == 'd':
        return date.day
    if fmt == 'MMM\nyyyy':
        return f'{months[date.month]}\n{date.year}'

def format_date(x, _):
    date = mdates.num2date(x)
    if date.day == 1 and date.month == 1:
        return mydate(date,'MMM\nyyyy')
    if date.day == 1:
        return mydate(date,'MMM')
    return mydate(date,'d')

class MyConciseDateFormatter(mticker.Formatter):
    def __init__(self, locator, show_offset=True):

        self._locator = locator

        # there are 6 levels with each level getting a specific format
        # 0: mostly years,  1: months,  2: days,
        # 3: hours, 4: minutes, 5: seconds

        self.formats = ['yyyy',  # ticks are mostly years
                        'MMM',          # ticks are mostly months
                        'd',          # ticks are mostly days
                        ]
        # fmt for zeros ticks at this level.  These are
        # ticks that should be labeled w/ info the level above.
        # like 1 Jan can just be labelled "Jan".  02:02:00 can
        # just be labeled 02:02.
        
        self.zero_formats = [''] + self.formats[:-1]
        self.offset_formats = ['',
                               'yyyy',
                               'MMM-yyyy'
                               ]

        self.offset_string = ''
        self.show_offset = show_offset

    def format_ticks(self, values):
        tickdatetime = [mdates.num2date(value) for value in values]
        tickdate = np.array([tdt.timetuple()[:6] for tdt in tickdatetime])

        # basic algorithm:
        # 1) only display a part of the date if it changes over the ticks.
        # 2) don't display the smaller part of the date if:
        #    it is always the same or if it is the start of the
        #    year, month, day etc.
        # fmt for most ticks at this level
        fmts = self.formats
        # format beginnings of days, months, years, etc.
        zerofmts = self.zero_formats
        # offset fmt are for the offset in the upper left of the
        # or lower right of the axis.
        offsetfmts = self.offset_formats
        show_offset = self.show_offset

        # determine the level we will label at:
        # mostly 0: years,  1: months,  2: days,
        # 3: hours, 4: minutes, 5: seconds, 6: microseconds
        for level in range(5, -1, -1):
            unique = np.unique(tickdate[:, level])
            if len(unique) > 1:
                # if 1 is included in unique, the year is shown in ticks
                if level < 2 and np.any(unique == 1):
                    show_offset = False
                break

        # level is the basic level we will label at.
        # now loop through and decide the actual ticklabels
        zerovals = [0, 1, 1, 0, 0, 0, 0]
        labels = [''] * len(tickdate)
        for nn in range(len(tickdate)):   
            if tickdate[nn][level] == zerovals[level]:
                fmt = zerofmts[level]
            else:
                fmt = fmts[level]

            labels[nn] = mydate(tickdatetime[nn],fmt)
            
        if show_offset:
            if(np.any(unique == 1)):
                level = level-1
            self.offset_string = mydate(tickdatetime[-1],offsetfmts[level])
            
        else:
            self.offset_string = ''

        return labels

    def get_offset(self):
        return self.offset_string



def plotting2(data):
    data = data.fillna('')

    name = data['name'][0]
    description = data['description'][0]
    prices = data['price'].asfreq('D')

    plt.rcParams['lines.linewidth'] = 2.5
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 18
    plt.rcParams["axes.labelpad"] = 12
    plt.rcParams["ytick.major.pad"] = -30
    plt.rcParams["ytick.alignment"] = 'bottom'
    plt.rcParams["xtick.major.size"] = 6
    plt.rcParams["xtick.minor.size"] = 6
    plt.rcParams["axes.titlepad"] = 30
    plt.rcParams["ytick.right"] = False
    plt.rcParams["ytick.left"] = False
    plt.rcParams["ytick.labelright"] = True
    plt.rcParams["ytick.labelleft"] = False
    plt.rcParams['axes.spines.left'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.bottom'] = True
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.grid.axis'] = 'y'

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(prices, color= '#18a1cd')

    ax.set_title(f"{name} {description}", loc='left')

    locator = mdates.AutoDateLocator()
    formatter = MyConciseDateFormatter(locator)
    
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    last_day = data.index[-1].strftime("%d-%m-%Y")

    ax.text(x=0.07, y=0.88, 
            s=f"Precio a {str(last_day)} de {prices.iloc[-1]}€",
            transform=fig.transFigure, 
            ha='left', 
            fontsize=14)
     
    ax.text(x=0.07, y=0.015, 
            s=f"@Merca_precio", 
            transform=fig.transFigure, 
            ha='left', 
            fontsize=14,
            alpha=.8)

    fig.tight_layout()
    
    plt.savefig("/tmp/chart.png", facecolor='white', bbox_inches='tight', pad_inches=0.2)

def generate_chart_url2(url):
    tb_by_url = os.getenv('tb_by_url')

    params = {
        'token': tb_by_url,
        'param': url
    }

    # print("In generate_chart_url")

    url = f'https://api.tinybird.co/v0/pipes/products_by_url.csv'
    
    response = requests.get(url, params=params)
    buffer = StringIO(response.text)
    data = pd.read_csv(buffer, index_col=0, parse_dates=True, na_values=['\\N'])

    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting2(data)
        return True


def generate_chart_basename2(basename):
    tb_by_basename = os.getenv('tb_by_basename')

    params = {
        'token': tb_by_basename,
        'param': basename
    }

    # print("In generate_chart_basename")
    url = f'https://api.tinybird.co/v0/pipes/products_by_basename.csv'

    response = requests.get(url, params=params)
    buffer = StringIO(response.text)
    data = pd.read_csv(buffer, index_col=0, parse_dates=True, na_values=['\\N'])

    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting2(data)
        return True

def proc_mention(client, api, tweet):
    if 'urls' in tweet['entities']:
        url = tweet.entities["urls"][0]['expanded_url']
        if "https://tienda.mercadona.es/product/" in url:
            if 'aceite-girasol-refinado-02o-hacendado' in url or not generate_chart_url2(url):
                basename = url.split('/')[-1]
                if not generate_chart_basename2(basename):
                    # print("Not in DB")
                    message = 'No he encontrado ese producto'
                    print("sending tweet")
                    client.create_tweet(in_reply_to_tweet_id=tweet.id, text=message)
                    return

            # print(f"sending tweet")
            media = api.media_upload(filename="/tmp/chart.png")
            message = "Aquí tienes el gráfico"
            print("sending tweet")
            client.create_tweet(in_reply_to_tweet_id=tweet.id, 
                text=message, 
                media_ids=[media.media_id])
        else:
            # print("not a mercadona url")
            message = 'No es una url válida'
            print("sending tweet")
            client.create_tweet(in_reply_to_tweet_id=tweet.id, text=message)
    else:
        # print("no urls")
        message = 'Hola 👋, en mi tweet fijado tienes explicado como funciona.'
        # print("sending tweet")
        # client.create_tweet(in_reply_to_tweet_id=tweet.id, text=message)

def proc_mentions(client, api):
    credentials = api.verify_credentials()
    print(f"Connected API 1 as: {credentials.id} {credentials.screen_name}")

    me = client.get_me()
    client_id = me.data.id
    username = me.data.username
    print(f"Connected API 2 as: {client_id} {username}")
    
    # not working with twitter free plan
    tweets = client.get_users_tweets(client_id,expansions='referenced_tweets.id')
    
    if tweets.data:
        # the are tweets
        if tweets.data[0].referenced_tweets:
            # there are answered tweets
            last_id = tweets.data[0].referenced_tweets[0].id
        else:
            # no answered tweets
            last_id = tweets.meta['newest_id']
    else:
        # there are no tweets
        last_id = client_id

    print(f"last_id: {last_id}")

    mentions = client.get_users_mentions(client_id, 
                                            since_id=last_id,
                                            tweet_fields='entities')
    print("get_users_mentions:")
    print(mentions)

    if mentions.data:
        for tweet in reversed(mentions.data):
            print(f"tweet: {tweet.id} {tweet}")
            proc_mention(client, api, tweet)

@app.get("/")
async def root():
    print("In root")
    client, api = start_client()
    proc_mentions(client, api)
    return "ok"

@app.post('/__space/v0/actions')
async def actions(request: Request):
    print("In actions")
    data = await request.json()
    print(data)
    event = data['event']
    if event['id'] == 'cron':
        client, api = start_client()
        proc_mentions(client, api)
