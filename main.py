import discord
import os
import sys
import urllib.request
import uuid
import validators

ffmpeg_command = 'ffmpeg -i {} -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" {}'
client = discord.Client()
api_key = os.environ.get('DISCORD_WEBM_BOT_KEY', sys.argv[1])

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
    # In order to bypass 403 forbidden error
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    url = ''
    if is_webm_in_content(message.content):
        url = message.content
    elif is_webm_in_attachments(message.attachments):
        url = message.attachments[0].url
    else:
        return

    file_name_webm, file_name_mp4 = download_file(url)
    await send_mp4_to_channel(message, file_name_mp4)

    print('Deleting files...')
    os.remove(file_name_webm)
    os.remove(file_name_mp4)

    print('Done!\n')

    
def is_webm_in_content(content):
    # TODO: Use a url regex to extract the url from the content
    return validators.url(content) and content.endswith('.webm')

def is_webm_in_attachments(attachments):
    return len(attachments) > 0 and attachments[0].url.endswith('.webm')

def download_file(url):
    file_name_webm = str(uuid.uuid4())
    file_name_mp4 = file_name_webm + '.mp4'

    print('Downloading: ' + url + '...')
    urllib.request.urlretrieve(url, file_name_webm)

    print('Converting webm to mp4...')
    os.system(ffmpeg_command.format(file_name_webm, file_name_mp4))

    return file_name_webm, file_name_mp4

async def send_mp4_to_channel(message, file_name_mp4):
    print('Sending mp4 to discord channel...')
    file = discord.File(file_name_mp4)
    await message.channel.send(file=file)

client.run(api_key)
