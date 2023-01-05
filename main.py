import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from io import StringIO
import os
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.dates as mdates
from datetime import date
from fastapi import FastAPI
from deta import App

app = App(FastAPI())

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

def plotting(data):
    data['date'] = pandas.to_datetime(data['date'])
    
    date = data["date"]
    price = data["price"]

    fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')
    ax.plot(date, price, linewidth=2.5, alpha=0.75)
    plt.grid(True)
    title_text = f"{data['name'][0]} {data['description'][0]}"
    ax.set_title(title_text, fontsize=16)
    ax.set_ylabel('Precio (€)')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %y"))
    
    ax.xaxis.set_minor_locator(mdates.DayLocator(15))
    #ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.margins(x=0)

    plt.savefig("/tmp/chart.png")

def plotting2(data):
    name = data['name'][0]
    description = data['description'][0]

    data_toplot = data['price']

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.set_title(f"{name} {description}", loc='left', fontsize=18)
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Precio", fontsize=12, labelpad=10)

    ax.spines[["top","left", "right"]].set_visible(False)
    ax.spines[["bottom"]].set_linewidth(1)

    ax.tick_params(width=1,labelsize=12, labelleft=False, labelright=True)
    ax.tick_params(axis='x', which='major', pad=4, length=8)
    ax.tick_params(axis='x', which='minor', pad=4, length=5, labelsize=12)
    ax.tick_params(axis='y', which='major', pad=-15, length=0)
    ax.tick_params(axis='y', which='minor', length=0)

    ax.xaxis.set_major_locator(mdates.DayLocator(1))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=(15)))
    # ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

    data_toplot.plot(ax=ax,legend=False, color="#18a1cd",linewidth=3,solid_capstyle="butt")

    for label in ax.get_yticklabels():
        label.set(horizontalalignment='center', verticalalignment='bottom')

    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=0, horizontalalignment='center')

    ax.set(xlabel=None)
    ax.grid(visible=True, axis='y', linewidth=1, color = '#A5A5A5')
    # ax.set_xlim(data.index[0])

    ax.autoscale(tight=False)
    plt.subplots_adjust(left=0.08, right= 0.95, bottom= 0.125)

    today = date.today().strftime("%d-%m-%Y")
    ax.text(x=.08, y=0.84, 
            s=f"Precio a {str(today)}", 
            transform=fig.transFigure, 
            ha='left', 
            fontsize=13, 
            alpha=.8)

    ax.text(x=.07, y=0, 
            s="@Merca_precio", 
            transform=fig.transFigure, 
            ha='left', 
            fontsize=14, 
            alpha=.7)
    
    plt.savefig("/tmp/chart.png", facecolor='white', bbox_inches='tight', pad_inches=0.2)

def generate_chart_url(url):
    tb_by_url = os.getenv('tb_by_url')

    params = {
        'token': tb_by_url,
        'param': url
    }

    # print("In generate_chart_url")

    url = f'https://api.tinybird.co/v0/pipes/products_by_url.csv'
    response = requests.get(url, params=params)
    data = pandas.read_csv(io.StringIO(response.text))
    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting(data)
        return True

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
    data = pd.read_csv(buffer, index_col=0, parse_dates=True)

    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting2(data)
        return True

def generate_chart_basename(basename):
    tb_by_basename = os.getenv('tb_by_basename')

    params = {
        'token': tb_by_basename,
        'param': basename
    }

    # print("In generate_chart_basename")
    url = f'https://api.tinybird.co/v0/pipes/products_by_basename.csv'
    response = requests.get(url, params=params)

    data = pandas.read_csv(io.StringIO(response.text))
    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting(data)
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
    data = pd.read_csv(buffer, index_col=0, parse_dates=True)

    if data.empty:
        # print('DataFrame is empty!')
        return False
    else:
        plotting(data)
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
        message = 'No has mandado una url'
        print("sending tweet")
        client.create_tweet(in_reply_to_tweet_id=tweet.id, text=message)

def proc_mentions(client, api):
    credentials = api.verify_credentials()
    print(f"Connected API 1 as: {credentials.id} {credentials.screen_name}")

    me = client.get_me()
    client_id = me.data.id
    username = me.data.username
    print(f"Connected API 2 as: {client_id} {username}")
    
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
    client, api = start_client()
    proc_mentions(client, api)
    return "ok"

@app.lib.cron()
def cron_job(event):
    client, api = start_client()
    proc_mentions(client, api)
    return "ok"