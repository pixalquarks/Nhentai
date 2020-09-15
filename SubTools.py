import aiohttp
import asyncio
import requests
import PySimpleGUI as sg
from PIL import Image, ImageTk
from io import BytesIO
# from Main import error_message_popup

def error_message_popup(errorMessage: str):

    layout = [[sg.Text(errorMessage)],
              [sg.OK()]]

    window = sg.Window('Error', layout)
    event, values = window.read()
    window.close()


def checkInternetConnection():
	try:
		r = requests.get("http://www.goolge.com", timeout=3)
		return True
	except:
		error_message_popup("Oops, looks like you are not connected to the internet, Please check your connection and retry")
		return False


async def waitForImage(session, url, first=False):
	async with session.get(url) as response:
		return await response.read()

# async def waitForImage(session, url, first=False):
# 	async with session.get(url) as response:
# 		return await response.read()

def getImage_data(filename: str, first=False, size=(400,400)):
	img = Image.open(filename)
	img.thumbnail(size)
	if first:
		bio = BytesIO()
		img.save(bio,format="PNG")
		del img 
		return bio.getvalue()
	return ImageTk.PhotoImage(img)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def getImageFromUrl(url, first=False,online=True,path=".\\NewTest.png"):
	if not online:
		return getImage_data(path,first=first)
	if not checkInternetConnection():
		return
	async with aiohttp.ClientSession() as session:
		html = await waitForImage(session, url)
		image = getImage_data(BytesIO(html),first)
		print(type(html))
		print(type(image))


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(getImageFromUrl("https://t.nhentai.net/galleries/710253/cover.jpg",first=True))
	print('okay')