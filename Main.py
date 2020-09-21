import PySimpleGUI as sg
import subprocess
import requests
import base64
import os
from NhentaiManager import NHentaiOP as NHentai
import SubTools as st
from PIL import Image, ImageTk
from io import BytesIO
from threading import Thread
import time
import Reader

nhentai = NHentai()
image_play = ".\\PLAY_.png"
image_pause = ".\\PAUSE_.png"
image_stop = ".\\STOP_.png"
image_start = ".\\START_.png"
image_end = ".\\END_.png"
image_next = ".\\NEXT_.png"
image_previous = ".\\PREVIOUS_.png"
isConnected = False
readingMode = False
autoRead = False
count = 0

current_thread = None
result_list = []
was_working = False
doujinData = {}
TIMEOUT = 1000

# Reading Speed Values
superSlow = 20
slow = 14
medium = 10
fast = 8
superFast = 5


def stopThisThing(printThis:str,nowPrintThis:str):
	print("Okay" + printThis)
	time.sleep(10)
	print("done" + nowPrintThis)
	return 10000

def get_Toggle_Read_Mode(change=None):
	global readingMode
	if change == None:
		return readingMode
	else:
		readingMode = not readingMode


def findhentai(hen_id:int,rslt_lst:list):
	print("Searching..")
	if not st.checkInternetConnection():
		return
	try:
		random_doujin: dict = nhentai._get_doujin(id=str(hen_id))
		rslt_lst.append(random_doujin)
		rslt_lst.append("search")
		print("Found Hentai")
		return
	except:
		#st.error_message_popup("Oops Coundn't fint the doujin you requested for, please try another code")
		return

def OpenDoujinInTheBrowser(link):
	if not st.checkInternetConnection():
		return
	try:
		subprocess.Popen(['C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe', link ])
	except:
		st.error_message_popup("Oops, I guess something went wrong")


def getImageFromUrl(url, first=False, online=False,path = ".\\NewTest.png"):
	if not online:
		return getImage_data(path,first=first)
	if not st.checkInternetConnection():
		return
	image_bytes = requests.get(url).content
	return getImage_data(BytesIO(image_bytes),first)


def getImage_data(filename: str, first=False, size=(400,400)):
	img = Image.open(filename)
	img.thumbnail(size)
	if first:
		bio = BytesIO()
		img.save(bio,format="PNG")
		del img 
		return bio.getvalue()
	return ImageTk.PhotoImage(img)



def UpdateStuff(doujinData: dict, window):
	window['_nameofhentai_'].update("  ".join(doujinData["title"]))
	window['_codeofhentai_'].update(doujinData["id"])
	window['_subnameofhentai_'].update(doujinData["secondary_title"])
	window['_artistButton_'].update(doujinData["artists"][0])
	window['_languages_'].update("  ".join(doujinData["languages"]))
	window['_tagsofhentai_'+sg.WRITE_ONLY_KEY].print(", ".join(doujinData['tags']))
	window['_pages_'].update(doujinData["pages"][0])
	#window["_coverImage_"].update(data=getImageFromUrl(doujinData["cover"],online=True))
	window["_coverImage_"].update(data=doujinData["cover"])
	URL = doujinData["url"]
	window["_info_"].update(visible=True)
	window["_cover_"].update(visible=True)

def toggleReadButtons(mainBtn: bool,navBtn: bool, window):
	window['_readOnline_'].update(visible=mainBtn)
	window['_download_'].update(visible=mainBtn)
	window['_play_'].update(visible=navBtn)
	window['_pause_'].update(visible=navBtn)
	window['_previous_'].update(visible=navBtn)
	window['_next_'].update(visible=navBtn)
	window['_start_'].update(visible=navBtn)
	window['_end_'].update(visible=navBtn)
	window['_stop_'].update(visible=navBtn)
	window['_autoRead_'].update(visible=mainBtn)


# def autoReading(images_list: list,speed: str,window):



Col_info = [
			  [sg.Text("Name: ",size=(15,1),background_color="#B7CECE"),sg.Text("Nothing Yet",key="_nameofhentai_",background_color="#B7CECE")],
			  [sg.Text("Code: ",size=(10,1),background_color="#B7CECE"),sg.Text("Nothing Yet", key="_codeofhentai_",background_color="#B7CECE")],
			  [sg.Text("Secondary Title: ",size=(15,1),background_color="#B7CECE"),sg.Text("Nothing Yet",key="_subnameofhentai_",background_color="#B7CECE")],
			  [sg.Text("Artist :",size=(15,1),background_color="#B7CECE"),sg.Button("Nothin yet",size=(20,1), key="_artistButton_",button_color=("#B7CECE","#B7CECE"))],
			  [sg.Text("languages: ",size=(15,1),background_color="#B7CECE"),sg.Button("Nothin yet",size=(15,1), key="_languages_",button_color=("#B7CECE","#B7CECE"))],
			  [sg.Text("Tags: ",size=(15,1),background_color="#B7CECE"),sg.MLine(key='_tagsofhentai_'+sg.WRITE_ONLY_KEY, size=(30,4))],
			  [sg.Text("Pages: ",size=(15,1),background_color="#B7CECE"),sg.Text("Nothing Yet",size=(10,1),key="_pages_",background_color="#B7CECE")]
			  ]



Col_image = [ 
				[sg.Image(data=getImageFromUrl("",first=True),key="_coverImage_")],
				[sg.pin(sg.Button("Read Doujin Online", key="_readOnline_")),sg.pin(sg.Button("Download", key="_download_")),
				sg.pin(sg.Checkbox('Auto Read', default=False,change_submits=True,enable_events=True, key='_autoRead_')),sg.pin(sg.Combo(['Super Slow', 'Slow', 'Medium','Fast','Super Fast'], key='_readSpeed_', visible=False))],
				[sg.pin(sg.Button("",image_filename=image_play,image_size=(20,20),pad=(3,3),key='_play_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_pause,image_size=(20,20),pad=(3,3),key='_pause_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_stop,image_size=(20,20),pad=(3,3),key='_stop_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_start,image_size=(40,20),pad=(3,3),key='_start_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_end,image_size=(40,20),pad=(3,3),key='_end_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_next,image_size=(20,20),pad=(3,3),key='_next_',button_color=("#B7CECE","#B7CECE"),visible=False)),
				sg.pin(sg.Button("",image_filename=image_previous,image_size=(20,20),pad=(3,3),key='_previous_',button_color=("#B7CECE","#B7CECE"),visible=False))]
				]

def test_menus():

    sg.theme('LightGreen')
    sg.set_options(element_padding=(0, 0))

    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit' ]],
                ['&Edit', ['&Paste', ['Special', 'Normal',], 'Undo'],],
                ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
                ['&Help', '&About...'],]

    right_click_menu = ['Unused', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']]


    # ------ GUI Defintion ------ #
    layout = [
              [sg.Menu(menu_def, tearoff=False, pad=(20,1))],
              [sg.Text("Enter the hentai id",size=(15,1)),sg.Input(size=(20,1),justification='right',key="-Id-"),sg.Button("Search")],
              [sg.pin(sg.Column(Col_info,key="_info_",visible=False, pad=(0,0))),sg.pin(sg.Column(Col_image,key="_cover_",visible=False))],
              # [sg.Output(size=(40,15))],
              [sg.Button("Take me to the page",size=(15,1),key="-Goto-")]
              ]

    window = sg.Window("NHentai-Prototype",
                       layout,
                       default_element_size=(12, 1),
                       return_keyboard_events=True,
                       grab_anywhere=False,
                       size=(800,800),
                       right_click_menu=right_click_menu,
                       default_button_element_size=(12, 1))

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = window.read(timeout=TIMEOUT)
        global doujinData
        global result_list
        # global current_thread
        global was_working
        
        if event is None or event == 'Exit':
        	return
        # ------ Process menu choices ------ #
        if event == 'About...':
            window.disappear()
            sg.popup('About this program','Version 1.0', 'PySimpleGUI rocks...', grab_anywhere=True)
            window.reappear()
        elif event == 'Open':
            filename = sg.popup_get_file('file to open', no_window=True)
            print(filename)
        elif event == 'Search':
        	if values['-Id-'] == '':
        		st.error_message_popup("Please Enter a code")
        	else:
        		was_working = True
        		print("Here in search")
        		window.FindElement('Search').update(disabled=True)
        		src_thread = Thread(target=findhentai,args=(values["-Id-"],result_list))
        		src_thread.start()
        		print("Searching")
        		# t = Thread(target=q_search.put,args=(findhentai(values["-Id-"]),))
        		# t.start()
        elif event == 'Properties':
            st.error_message_popup()
        elif event == '-Goto-':
        	try:
        		OpenDoujinInTheBrowser(doujinData['url'])
        	except:
        		st.error_message_popup("Please Search a doujin first")
        elif event == '_readOnline_':
        	#toggleReadButtons(False,True,window)
        	#get_Toggle_Read_Mode(change=True)
        	Reader.Reader(doujinData["images"],autoRead=True,readSpeed=10)
        elif event == '_download_':
        	# global result_list
        	# global current_thread
        	# global was_working
        	was_working = True
        	window.FindElement('_download_').update(disabled=True)
        	dwn_thread = Thread(target=st.download,args=(doujinData["title"][1],doujinData["images"],result_list))
        	dwn_thread.start()

        if get_Toggle_Read_Mode():
        	global count
        	if event == '_stop_':
        		toggleReadButtons(True,False,window)
        		get_Toggle_Read_Mode(change=True)
        	elif event == '_next_':
        		count+=1
        		window["_coverImage_"].update(data=getImageFromUrl(doujinData["images"][count],online=True))
        	elif event == '_previous_':
        		count-=1
        		window["_coverImage_"].update(data=getImageFromUrl(doujinData["images"][count],online=True))
        	elif event == '_start_':
        		count = 0
        		window["_coverImage_"].update(data=getImageFromUrl(doujinData["images"][count],online=True))
        	elif event == '_end_':
        		count = len(doujinData["images"]) - 1
        		window["_coverImage_"].update(data=getImageFromUrl(doujinData["images"][count],online=True))	
        isAutoReadChecked = values['_autoRead_']	
        if isAutoReadChecked == True:
        	window['_readSpeed_'].update(visible=True)
        elif isAutoReadChecked == False:
        	window['_readSpeed_'].update(visible=False)
        # if q_search.empty():
        # 	pass
        # else:
        # 	doujinData = q_search.get()
        # 	if doujinData != None:
        # 		UpdateStuff(doujinData,window)
        if was_working:
        	checkThread(window)

def checkThread(window):
	# global current_thread
	global result_list
	global was_working
	global doujinData
	# if not was_working:
	# 	return
	# if current_thread.is_alive():
	# 	return
	if len(result_list) > 1:
		if result_list[-1] == 'download':
			was_working = False
			message = "Successfully downloaded " + str(result_list[0] - result_list[1]) + " out of " + str(result_list[0]) + " images in " + str(result_list[2]) + " seconds "
			#sg.popup("Successfully downloaded " + str(result_list[0] - result_list[1]) + " out of " + str(result_list[0]) + " images in " + str(result_list[2]) + " seconds ")
			st.encryptor_window(message,doujinData["title"][1])
			result_list = []
			current_thread = None
			window.FindElement("_download_").update(disabled=False)
			return
		elif result_list[-1] == 'search':
			doujinData = result_list[0]
			if doujinData != None:
				UpdateStuff(doujinData,window)
			result_list = []
			current_thread = None
			was_working = False
			window.FindElement('Search').update(disabled=False)
			return




        # elif event == '_readOnline_':
isConnected = st.checkInternetConnection()
test_menus()




# things to remember
# sg.pin function helps to keep column not to stack over each other when made invisible and visible again.