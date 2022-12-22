import discord
import asyncio
import requests
import os
import json

## Load our bot token:
# Open the JSON file
with open('token.json', 'r') as f:
    # Load the data from the file
    data = json.load(f)

## Set intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

asked_for_post_limit = False

def scan_subreddit(subreddit_name):
    # Use the Reddit API to get the latest posts from the subreddit
    headers = {'User-Agent': 'myBot/0.0.1'}
    url = f'https://www.reddit.com/r/{subreddit_name}/new.json'
    res = requests.get(url, headers=headers)
    subreddit_posts = res.json()['data']['children']
    return subreddit_posts

def download_images(subreddit_posts):
    # Download the images from the subreddit posts
    images = []
    for post in subreddit_posts:
        image_url = post['data']['url']
        if image_url.endswith('.jpg') or image_url.endswith('.png'):
            res = requests.get(image_url)
            images.append(res.content)
    return images

async def upload_images(channel, images, limit):
    # Iterate over the images and upload each one to the Discord channel
    i = 1
    for image in images:
        if (i > limit): return
        i += 1
        with open('image.jpg', 'wb') as f:
            f.write(image)
        with open('image.jpg', 'rb') as f:
            await channel.send(file=discord.File(f))


@client.event
async def on_message(message):
    # Check if the message is from the bot itself
    if message.content is not None:
        message_content = message.content
    else:
        message_content = "The message has no content"
    print(message_content)

    if message.author == client.user:
        return

    if message.content.startswith('!scan'):
        # Ask a question
        await message.channel.send("What subreddit do you want to scan?")

        # Wait for a response from the user
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        try:
            subreddit = await client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await message.channel.send("You didn't respond in time :(")
            return
        
        # Store the answer in a variable
        subreddit_name = subreddit.content

        # Print the answer to the console
        print(f'{subreddit.author} responded with "{subreddit_name}"')

        # Ask the user for the number of posts to scan
        await message.channel.send("How many posts do you want to scan?")

        # Wait for a response from the user
        try:
            post_limit_response = await client.wait_for('message', check=check, timeout=30.0)
            post_limit_response = post_limit_response.content
            print(post_limit_response)
        except asyncio.TimeoutError:
            await message.channel.send("You didn't respond in time :(")
            return

    # Store the answer in a variable
        # Scan the subreddit for new posts
        subreddit_posts = scan_subreddit(subreddit_name)
        # Download the posts with images
        images = download_images(subreddit_posts)
        # Upload the images
        await upload_images(message.channel, images, int(post_limit_response))

client.run(data["key"])