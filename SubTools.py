import aiohttp
import asyncio
import aiofiles
import requests
import os
import PySimpleGUI as sg
from PIL import Image, ImageTk
from io import BytesIO
import time
# from Main import error_message_popup


def checkInternetConnection():
	try:
		r = requests.get("http://www.goolge.com", timeout=3)
		return True
	except:
		error_message_popup("Oops, looks like you are not connected to the internet, Please check your connection and retry")
		return False

def getImageFromUrlSync(url, first=False, online=False,size=(400,400),path = ".\\NewTest.png"):
  if not online:
    return getImage_dataSync(path,first=first)
  if not checkInternetConnection():
    return
  image_bytes = requests.get(url).content
  return getImage_dataSync(BytesIO(image_bytes),first,size=size)


def getImage_dataSync(filename: str, first=False, size=(400,400)):
  img = Image.open(filename)
  img.thumbnail(size)
  if first:
    bio = BytesIO()
    img.save(bio,format="PNG")
    del img 
    return bio.getvalue()
  return ImageTk.PhotoImage(img)



def error_message_popup(errorMessage: str):

    layout = [[sg.Text(errorMessage)],
              [sg.OK()]]

    window = sg.Window('Error', layout)
    event, values = window.read()
    window.close()





async def waitForImage(session, url, first=False):
	async with session.get(url) as response:
		return await response.read()

# async def waitForImage(session, url, first=False):
# 	async with session.get(url) as response:
# 		return await response.read()

# def getImage_data(filename: str, first=False, size=(400,400)):
# 	img = Image.open(filename)
# 	img.thumbnail(size)
# 	if first:
# 		bio = BytesIO()
# 		img.save(bio,format="PNG")
# 		del img 
# 		return bio.getvalue()
# 	return ImageTk.PhotoImage(img)

async def fetch(session, url, page_no:str, list_failed):
    async with session.get(url) as resp:
        if resp.status == 200:

            async with aiofiles.open(page_no, mode='wb') as f:
                await f.write(await resp.read())
                await f.close()
        else:
        	list_failed.append(page_no)

async def getImageFromUrl(url, first=False,online=True,path=".\\NewTest.png"):
	if not online:
		return getImage_data(path,first=first)
	if not checkInternetConnection():
		return
	async with aiohttp.ClientSession() as session:
		html = await waitForImage(session, url)
		image = getImage_dataSync(BytesIO(html),first)
		return image


async def download_images(image_urls:list,list_failed:list):
    tasks = []
    count = 1
    headers = {
        "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        for image in image_urls:
        	count += 1
        	tasks.append(await fetch(session, image, "Page - " + str(count) + ".jpg",list_failed))
    data = await asyncio.gather(*tasks)

def download(name_of_hentai:str,image_urls:list,result_list:list):
	if not checkInternetConnection():
		return
	t1 = time.time()
	list_failed = []
	path_original = os.getcwd()
	print(path_original)
	path = path_original + "\\" + name_of_hentai
	try:
		os.mkdir(path)
	except FileExistsError as e:
		print("Folder already exists")
	finally:
		os.chdir(path)
		print("path changed")
	try:
		asyncio.run(download_images(image_urls, list_failed))
	except TypeError as e:
		pass
	os.chdir(path)
	print("Path changes back to normal")
	tt = time.time() - t1
	result_list.append(len(image_urls))
	result_list.append(len(list_failed))
	result_list.append(tt)
	result_list.append("download")
	del list_failed
	#error_message_popup("Downloaded " + str(len(image_urls) - len(list_failed)) + "out of " + str(len(image_urls)) + "images. Total time taken to download was " + str(tt) + "seconds")
	print(tt)

def getCoverData(url:str):
	# loop = asyncio.new_event_loop()
	# asyncio.set_event_loop(loop)
	try:
		image = asyncio.run(getImageFromUrl(url,first=True))
	except:
		pass
	# loop.close()
	return image

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(getImageFromUrl("https://t.nhentai.net/galleries/710253/cover.jpg",first=True))
	print('okay')