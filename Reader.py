import PySimpleGUI as sg
import SubTools as st
import time
from threading import Thread


# all the buttons 
image_play = ".\\PLAY_.png"
image_pause = ".\\PAUSE_.png"
image_stop = ".\\STOP_.png"
image_start = ".\\START_.png"
image_end = ".\\END_.png"
image_next = ".\\NEXT_.png"
image_previous = ".\\PREVIOUS_.png"


test_image_list = ['https://i.nhentai.net/galleries/1735962/1.jpg', 'https://i.nhentai.net/galleries/1735962/2.jpg', 
                    'https://i.nhentai.net/galleries/1735962/3.jpg','https://i.nhentai.net/galleries/1735962/4.jpg'] 
                    # 'https://i.nhentai.net/galleries/1735962/5.jpg','https://i.nhentai.net/galleries/1735962/6.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/7.jpg','https://i.nhentai.net/galleries/1735962/8.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/9.jpg','https://i.nhentai.net/galleries/1735962/10.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/11.jpg','https://i.nhentai.net/galleries/1735962/12.jpg',
                    # 'https://i.nhentai.net/galleries/1735962/13.jpg',
                    # 'https://i.nhentai.net/galleries/1735962/14.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/15.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/16.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/17.jpg', 
                    # 'https://i.nhentai.net/galleries/1735962/18.jpg'

WIDTH = 720
HEIGHT = 1080

TIMEOUT = 1000
READING_MODE = 'manual'
needToLoadNextImage = False
Online = True
First = True
counter = 0
updated_img_data = None
running = False

Col_image = [
        [sg.pin(sg.Button("Read Doujin Online", key="_readOnline_")),sg.pin(sg.Button("Download", key="_download_")),
        sg.pin(sg.Checkbox('Auto Read', default=False,change_submits=True,enable_events=True, key='_autoRead_')),sg.pin(sg.Combo(['Super Slow', 'Slow', 'Medium','Fast','Super Fast'], key='_readSpeed_', visible=False))],
        [sg.pin(sg.Button("",image_filename=image_play,image_size=(20,20),pad=(3,3),key='_play_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_pause,image_size=(20,20),pad=(3,3),key='_pause_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_stop,image_size=(20,20),pad=(3,3),key='_stop_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_start,image_size=(40,20),pad=(3,3),key='_start_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_end,image_size=(40,20),pad=(3,3),key='_end_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_next,image_size=(20,20),pad=(3,3),key='_next_',button_color=("#B7CECE","#B7CECE"))),
        sg.pin(sg.Button("",image_filename=image_previous,image_size=(20,20),pad=(3,3),key='_previous_',button_color=("#B7CECE","#B7CECE")))]
        ]

def autoReader(readSpeed:int,image_list:list):
    global Online
    global counter
    global First
    global needToLoadNextImage
    global updated_img_data
    global running
    print("Inside auto read func")
    while True:
        t1 = time.time()
        img_url = image_list[counter]
        img_data = st.getImageFromUrlSync(img_url,first=First,online=Online)
        if not running:
            updated_img_data = img_data
            print("Updated image data")
            counter += 1
            running = True
            needToLoadNextImage = True
            continue
        t2 = time.time()
        t_sleep = readSpeed - (t2 - t1) - 0.5
        time.sleep(t_sleep)
        updated_img_data = img_data
        counter+=1
        needToLoadNextImage = True
        if counter == len(image_list) - 1:
            return
        print("Updated image data from outside if ")





def Reader(image_list:list,autoRead=False,readSpeed=0):
    global updated_img_data
    print("Inside The reader")

    sg.theme('LightGreen')
    sg.set_options(element_padding=(0, 0))
    if autoRead:
        print("Inside the Thread")
        Thread(target=autoReader,args=(readSpeed,image_list)).start()
        print("Thread Started")
        print("Sleeping...")
        time.sleep(6)
        print("Awaken")
    print("Out of the if")

    # ------ Menu Definition ------ #
    # menu_def = [['&File', ['&Open', '&Save', '&Properties', 'E&xit' ]],
    #             ['&Edit', ['&Paste', ['Special', 'Normal',], 'Undo'],],
    #             ['&Toolbar', ['---', 'Command &1', 'Command &2', '---', 'Command &3', 'Command &4']],
    #             ['&Help', '&About...'],]

    # right_click_menu = ['Unused', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']]


    # ------ GUI Defintion ------ #
    layout = [
              [sg.Image(data=updated_img_data,key='_image_')],
              #[sg.Image(data=st.getImageFromUrlSync(None,first=True,online=False))],
              #[sg.Text("Enter the hentai id",size=(15,1)),sg.Input(size=(20,1),justification='right',key="-Id-"),sg.Button("Search")],
              [sg.pin(sg.Column(Col_image))]
              #[sg.pin(sg.Column(Col_info,key="_info_",visible=False, pad=(0,0))),sg.pin(sg.Column(Col_image,key="_cover_",visible=False))],
              # [sg.Output(size=(40,15))],
              #[sg.Button("Take me to the page",size=(15,1),key="-Goto-")]
              ]
    global WIDTH
    global HEIGHT

    window = sg.Window("NHentai-Prototype",
                       layout,
                       default_element_size=(12, 1),
                       return_keyboard_events=True,
                       grab_anywhere=False,
                       size=(WIDTH,HEIGHT),
                       #right_click_menu=right_click_menu,
                       default_button_element_size=(12, 1))
    print("Window created")

    while True:
        global needToLoadNextImage
        events, values = window.read(timeout=1000)
        if events == None or events == 'Exit':
            return

        if needToLoadNextImage:
            print("Updating image data")
            window.FindElement('_image_').update(data=updated_img_data)
            needToLoadNextImage = False

if __name__ == '__main__':
  Reader(test_image_list,autoRead=True,readSpeed=10)