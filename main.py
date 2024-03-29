import configparser
import cProfile
import os
import pickle
import pstats
import time
import tkinter
import customtkinter
import tkinter.font
from ast import literal_eval
from datetime import datetime
from random import randint
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from pymongo import MongoClient
from tkcolorpicker import askcolor
from webcolors import hex_to_name

softwareversion = "Beta 1.1"


config = configparser.ConfigParser()
config.read("config.txt")


print("Connecting to database...")

dbclient = MongoClient(str("mongodb://" + str(config['Database']['Username']) + ":" + str(config['Database']['Password']) + "@" + str(config['Database']['IP']) + ":" + str(config['Database']['Port']) + "/?appname=NetPOS&directConnection=true&ssl=false"))
database = dbclient["NetPOS"]

print("Checking database structure...")
databaselist = database.list_collection_names()

if not 'pages' in databaselist:
    print("Page collection does not exist. Creating...")
    database.create_collection("pages")
    pagescol = database["pages"]
    pagetemplate = {
        "PageID": randint(1, 9999999999999999),
        "Name": str(config['NetPOS']['DefaultPage']),
        "BackgroundColor": "#87CFEC",
        "ForegroundColor": "#FFD993",
        "Buttons": [],
        "PermissionListType": "Disabled",
        "PermissionList": []
    }
    pagescol.insert_one(pagetemplate)
if not 'buttons' in databaselist:
    print("Button collection does not exist. Creating...")
    database.create_collection("buttons")
if not 'items' in databaselist:
    print("Item collection does not exist. Creating...")
    database.create_collection("items")
if not 'users' in databaselist:
    print("User collection does not exist. Creating...")
    database.create_collection("users")



customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

root = customtkinter.CTk()
currentpage = config['NetPOS']['DefaultPage']
currentcheck = 0
currentuser = 0

default_font = tkinter.font.nametofont("TkDefaultFont")
default_font.configure(family=config['NetPOS']['DefaultFont'])
default_font.configure(size=config['NetPOS']['DefaultFontSize'])


root.geometry("1920x1080")
root.title("NetPOS")

blankimage = PhotoImage()
keyboardicon = PhotoImage(file = "icons/keyboard.png")
settingsicon = PhotoImage(file = "icons/settings.png")
buttonwidgets = []
settingwidgets = []
miscwidgets = []
buttoncommands = {}
InEditMode = False

def OpenKeyboard():
    #This method will open an onscreen keyboard
    os.system('/usr/bin/onboard')

def log(event,additionalinfo="None"):
    global currentuser
    print("[" + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + " on " + str(config['NetPOS']['Alias']) + "] User " + str(currentuser) + ": " + event + " (Extra Info: " + additionalinfo + ")" )

def GetCheckInfo(checkid):
    pass

def GetUserInfo(uid):
    pass

def ToggleEditMode():
    global InEditMode
    if InEditMode:
        #1print("Edit Mode Off")
        log("Toggle Edit Mode", "Status: Off")
        Draw(currentpage,False)
        InEditMode = False
    else:
        #1print("Edit Mode On")
        log("Toggle Edit Mode", "Status: On")
        Draw(currentpage, True)
        InEditMode = True

highlightedbuttons = []

newbutton_textvar = StringVar()
newbutton_textsizevar = StringVar()
newbutton_textcolor = StringVar()
newbutton_buttonwidth = StringVar()
newbutton_buttonheight = StringVar()
newbutton_buttoncolor = StringVar()
newbutton_linkeditem = StringVar()
newbutton_linkedpage = StringVar()
newbutton_linkedscript = StringVar()
settingwidgets = []

buttoneditorwidgets = []

affectedbuttoncontainer = []


def EditButton(buttonID,emtype):
    global buttondictionary, highlightedbuttons, currentpage, affectedbuttoncontainer, settingwidgets
    UpdateItemNames()
    UpdatePageNames()
    for button in affectedbuttoncontainer:
        affectedbuttoncontainer.remove(button)
    Draw(currentpage,True)
    if emtype == "Button":
        additionalbuttoninfo = database.buttons.find_one({'ButtonID':int(buttonID)})
        #1print(additionalbuttoninfo)
        buttonobject = buttondictionary[str(buttonID)]
        oldheight = buttonobject.winfo_height()
        #1print(oldheight)
        oldwidth = buttonobject.winfo_width()
        #1print(oldwidth)
        affectedbuttoncontainer.append(buttonobject)
        buttonobject.config(relief="groove", highlightbackground="#0052FF", highlightthickness=5,
                            width=int(oldwidth) - 15,
                            height=int(oldheight) - 15)
        #1print("Opening editor for button " + str(buttonID))

        newbutton_textvar.set(additionalbuttoninfo["Text"])
        newbutton_textsizevar.set(additionalbuttoninfo["FontSize"])
        newbutton_textcolor.set(additionalbuttoninfo["FG"])
        newbutton_buttonwidth.set(additionalbuttoninfo["Width"])
        newbutton_buttonheight.set(additionalbuttoninfo["Height"])
        newbutton_buttoncolor.set(additionalbuttoninfo["BG"])
        newbutton_linkeditem.set(additionalbuttoninfo["LinkedItem"])
        newbutton_linkedpage.set(additionalbuttoninfo["LinkedPage"])
        newbutton_linkedscript.set(additionalbuttoninfo["LinkedScript"])

        textsizeoptions = ["Smallest","Smaller","Small","Normal","Big","Bigger","Biggest"]

        buttonwidthoptions = []
        buttonheightoptions = []

        buttonitemoptions = []
        buttonpageoptions = []
        buttonscriptoptions = []

        buttonitemoptions.append("None")
        buttonpageoptions.append("None")
        buttonscriptoptions.append("None")

        for i in range (1,((int(config["NetPOS"]["Columns"])+1)-int(additionalbuttoninfo["Column"]))):
            buttonwidthoptions.append(str(i))
        for i in range (1,((int(config["NetPOS"]["Rows"])+1)-int(additionalbuttoninfo["Row"]))):
            buttonheightoptions.append(str(i))

        buttonobject.config(text="",textvariable=newbutton_textvar)

        removebuttonbutton = customtkinter.CTkButton(root, image=blankimage, width=200, height=80, font=("OpenSans", 20), text_color="black", text="Delete Button", fg_color="#FF6262", command=lambda btn=buttonID: DeleteButton(btn))
        removebuttonbutton.place(x=int(config['NetPOS']['ItemListRoot_X'])+165,y=int(config['NetPOS']['ItemListRoot_Y'])+700)
        savebuttonbutton = customtkinter.CTkButton(root, image=blankimage, width=200, height=80, font=("OpenSans", 20), text_color="black",
                                    text="Save Changes", fg_color="#80FF62",
                                    command=lambda btn=buttonID: SaveButton(btn))
        savebuttonbutton.place(x=int(config['NetPOS']['ItemListRoot_X']) + 165,
                                 y=int(config['NetPOS']['ItemListRoot_Y']) + 10)
        buttontextlabel = customtkinter.CTkLabel(root,text="Text:",font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])),text_color="black",fg_color=pagebgcolor)
        buttontextlabel.place(x=int(config['NetPOS']['ItemListRoot_X']),y=int(config['NetPOS']['ItemListRoot_Y'])+150)
        textcolorlabel = customtkinter.CTkLabel(root, text="Text Color:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                                fg_color=pagebgcolor)
        textcolorlabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                              y=int(config['NetPOS']['ItemListRoot_Y']) + 250)

        fontsizelabel = customtkinter.CTkLabel(root, text="Text Size:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                                fg_color=pagebgcolor)
        fontsizelabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                              y=int(config['NetPOS']['ItemListRoot_Y']) + 200)
        buttontypelabel = customtkinter.CTkLabel(root, text="Button Size:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                              fg_color=pagebgcolor)
        buttontypelabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                            y=int(config['NetPOS']['ItemListRoot_Y']) + 300)
        buttoncolorlabel = customtkinter.CTkLabel(root, text="Button Color:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                                fg_color=pagebgcolor)
        buttoncolorlabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                              y=int(config['NetPOS']['ItemListRoot_Y']) + 350)
        itemlabel = customtkinter.CTkLabel(root, text="Linked Item:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                                 fg_color=pagebgcolor)
        itemlabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                               y=int(config['NetPOS']['ItemListRoot_Y']) + 400)
        pagelabel = customtkinter.CTkLabel(root, text="Linked Page:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                          fg_color=pagebgcolor)
        pagelabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                        y=int(config['NetPOS']['ItemListRoot_Y']) + 450)
        scriptlabel = customtkinter.CTkLabel(root, text="Linked Script:", font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black",
                          fg_color=pagebgcolor)
        scriptlabel.place(x=int(config['NetPOS']['ItemListRoot_X']),
                        y=int(config['NetPOS']['ItemListRoot_Y']) + 500)

        buttontexttextbox = customtkinter.CTkEntry(textvariable=newbutton_textvar,width=10,font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])))
        buttontexttextbox.place(x=int(config['NetPOS']['ItemListRoot_X'])+300,y=int(config['NetPOS']['ItemListRoot_Y'])+150)

        textsizedropdownbox = customtkinter.CTkOptionMenu(root, newbutton_textsizevar, *textsizeoptions, command=lambda trash=None: ButtonPreviewTextResize(trash))
        textsizedropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        textsizedropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X'])+300,y=int(config['NetPOS']['ItemListRoot_Y'])+200)

        textcolorselector = customtkinter.CTkButton(image=blankimage,width=100,height=35,fg_color=newbutton_textcolor.get(),command=lambda btnID=buttonID, ctype="text": ColorSelectorHandler(ctype,btnID))
        textcolorselector.place(x=int(config['NetPOS']['ItemListRoot_X'])+300,y=int(config['NetPOS']['ItemListRoot_Y'])+250)

        buttonwidthdropdownbox = customtkinter.CTkOptionMenu(root, newbutton_buttonwidth, *buttonwidthoptions, command=lambda trash=None: ButtonPreviewResize(trash))
        buttonwidthdropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        buttonwidthdropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X']) + 300,
                                  y=int(config['NetPOS']['ItemListRoot_Y']) + 300)

        buttonheightdropdownbox = customtkinter.CTkOptionMenu(root, newbutton_buttonheight, *buttonheightoptions, command=lambda trash=None: ButtonPreviewResize(trash))
        buttonheightdropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        buttonheightdropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X']) + 410,
                                     y=int(config['NetPOS']['ItemListRoot_Y']) + 300)

        bylabel = customtkinter.CTkLabel(text_color="black",fg_color=str(pagebgcolor),text="by",font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        bylabel.place(x=int(config['NetPOS']['ItemListRoot_X']) + 365,
                                     y=int(config['NetPOS']['ItemListRoot_Y']) + 310)

        buttoncolorselector = customtkinter.CTkButton(image=blankimage, fg_color=newbutton_buttoncolor.get(), width=100, height=35,command=lambda btnID=buttonID, ctype="button": ColorSelectorHandler(ctype,btnID))
        buttoncolorselector.place(x=int(config['NetPOS']['ItemListRoot_X']) + 300,
                                y=int(config['NetPOS']['ItemListRoot_Y']) + 350)

        buttonitemoptions = ["None"]
        for item in itemoptions:
            buttonitemoptions.append(item["Name"])

        itemlinkdropdownbox = customtkinter.CTkOptionMenu(root, newbutton_linkeditem, *buttonitemoptions)
        itemlinkdropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        itemlinkdropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X']) + 300,
                                  y=int(config['NetPOS']['ItemListRoot_Y']) + 400)

        buttonpageoptions = ["None"]
        for page in pageoptions:
            buttonpageoptions.append(page)
        pagelinkdropdownbox = customtkinter.CTkOptionMenu(root, newbutton_linkedpage, *buttonpageoptions)
        pagelinkdropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        pagelinkdropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X']) + 300,
                                  y=int(config['NetPOS']['ItemListRoot_Y']) + 450)

        scriptlinkdropdownbox = customtkinter.CTkOptionMenu(root, newbutton_linkedscript, *buttonscriptoptions)
        scriptlinkdropdownbox.config(font=("OpenSans",int(config['NetPOS']['DropdownBoxFontSize'])))
        scriptlinkdropdownbox.place(x=int(config['NetPOS']['ItemListRoot_X']) + 300,
                                  y=int(config['NetPOS']['ItemListRoot_Y']) + 500)

        settingwidgets = []
        settingwidgets.append(textcolorselector)
        settingwidgets.append(buttoncolorselector)

        miscwidgets.append(scriptlinkdropdownbox)
        miscwidgets.append(pagelinkdropdownbox)
        miscwidgets.append(itemlinkdropdownbox)
        miscwidgets.append(bylabel)
        miscwidgets.append(buttoncolorselector)

        miscwidgets.append(buttonwidthdropdownbox)
        miscwidgets.append(buttonheightdropdownbox)
        miscwidgets.append(textcolorselector)

        miscwidgets.append(textsizedropdownbox)
        miscwidgets.append(removebuttonbutton)
        miscwidgets.append(buttontexttextbox)
        miscwidgets.append(textcolorlabel)
        miscwidgets.append(savebuttonbutton)
        miscwidgets.append(buttoncolorlabel)
        miscwidgets.append(fontsizelabel)
        miscwidgets.append(buttontypelabel)
        miscwidgets.append(buttontextlabel)
        miscwidgets.append(itemlabel)
        miscwidgets.append(pagelabel)
        miscwidgets.append(scriptlabel)

        buttoneditorwidgets.append(scriptlinkdropdownbox)
        buttoneditorwidgets.append(pagelinkdropdownbox)
        buttoneditorwidgets.append(itemlinkdropdownbox)
        buttoneditorwidgets.append(bylabel)
        buttoneditorwidgets.append(buttoncolorselector)

        buttoneditorwidgets.append(buttonwidthdropdownbox)
        buttoneditorwidgets.append(buttonheightdropdownbox)
        buttoneditorwidgets.append(textcolorselector)

        buttoneditorwidgets.append(textsizedropdownbox)
        buttoneditorwidgets.append(removebuttonbutton)
        buttoneditorwidgets.append(buttontexttextbox)
        buttoneditorwidgets.append(textcolorlabel)
        buttoneditorwidgets.append(savebuttonbutton)
        buttoneditorwidgets.append(buttoncolorlabel)
        buttoneditorwidgets.append(fontsizelabel)
        buttoneditorwidgets.append(buttontypelabel)
        buttoneditorwidgets.append(buttontextlabel)
        buttoneditorwidgets.append(itemlabel)
        buttoneditorwidgets.append(pagelabel)
        buttoneditorwidgets.append(scriptlabel)
    if emtype == "Slot":
        buttonobject = buttondictionary[str(buttonID)]
        buttonobject.config(relief="groove", highlightbackground="#0052FF", highlightthickness=5,
                            width=int(config['NetPOS']['ButtonWidth']) - 10,
                            height=int(config['NetPOS']['ButtonHeight']) - 10)
        #1print("Showing edit option for button in slot " + str(buttonID))
        createbuttonbutton = customtkinter.CTkButton(root, image=blankimage, width=200, height=80, font=("OpenSans", 20), text_color="black", text="Create Button", fg_color="#80FF62", command=lambda slot=buttonID: CreateNewButton(slot))
        createbuttonbutton.place(x=int(config['NetPOS']['ItemListRoot_X'])+165,y=int(config['NetPOS']['ItemListRoot_Y'])+10)
        miscwidgets.append(createbuttonbutton)
        buttoneditorwidgets.append(createbuttonbutton)
    ##1print(buttonobject)

def ButtonPreviewTextResize(trasharg):
    global affectedbuttoncontainer
    buttonsize = int(config['NetPOS']['DefaultFontSize'])
    buttonoptionsize = newbutton_textsizevar.get()
    if buttonoptionsize == "Smaller":
        buttonsize = int(round(buttonsize / 2))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    elif buttonoptionsize == "Smallest":
        buttonsize = int(round(buttonsize / 3))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    elif buttonoptionsize == "Small":
        buttonsize = int(round(((buttonsize / 2) + buttonsize) / 2))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    elif buttonoptionsize == "Big":
        buttonsize = int(round(((buttonsize * 2) + buttonsize) / 2))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    elif buttonoptionsize == "Bigger":
        buttonsize = int(round(buttonsize * 2))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    elif buttonoptionsize == "Biggest":
        buttonsize = int(round(buttonsize * 3))
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))
    else:
        buttonsize = int(config['NetPOS']['DefaultFontSize'])
        affectedbuttoncontainer[0].config(font=(config['NetPOS']['DefaultFont'], buttonsize))

def ButtonPreviewResize(trasharg):
    global affectedbuttoncontainer
    affectedbuttoncontainer[0].lift()
    affectedbuttoncontainer[0].config(wraplength=str(int(config['NetPOS']['ButtonWidth']) + (
                (int(newbutton_buttonwidth.get()) - 1) * (
                    int(config['NetPOS']['VerticalGap']) + int(config['NetPOS']['ButtonWidth'])))),width=str(int(config['NetPOS']['ButtonWidth']) + (
                (int(newbutton_buttonwidth.get()) - 1) * (
                    int(config['NetPOS']['VerticalGap']) + int(config['NetPOS']['ButtonWidth'])))), height=str(
        int(config['NetPOS']['ButtonHeight']) + ((int(newbutton_buttonheight.get()) - 1) * (
                    int(config['NetPOS']['HorizontalGap']) + int(config['NetPOS']['ButtonHeight'])))))

def DeleteButton(buttonID):
    global buttondictionary, highlightedbuttons, currentpage
    #1print("Deleting Button " + str(buttonID))
    database.buttons.delete_one({'ButtonID': buttonID})
    Draw(currentpage, True)

def SaveButton(buttonID):
    global buttondictionary, highlightedbuttons, currentpage
    database.buttons.update_one({'ButtonID': buttonID},{'$set':{"Text":newbutton_textvar.get(),"FG":newbutton_textcolor.get(),"BG":newbutton_buttoncolor.get(),"Width":newbutton_buttonwidth.get(),"Height":newbutton_buttonheight.get(),"FontSize":newbutton_textsizevar.get(),"LinkedItem":newbutton_linkeditem.get(),"LinkedPage":newbutton_linkedpage.get(),"LinkedScript":newbutton_linkedscript.get()}})
    log("Edited Button",
        str("Page '" + currentpage.lower() + "' Button '" + str(buttonID) + "' aka '" + str(newbutton_textvar.get()) + "'"))
    EditButton(buttonID,"Button")
    pass


def ColorSelectorHandler(colortype,pageID=None):
    global affectedbuttoncontainer, settingwidgets, previewboxcontainer, pagebgcolorcontainer, pagefgcolorcontainer, pagetoedit
    returnedcolor = askcolor()
    print(returnedcolor)
    pageID = pagetoedit
    if not returnedcolor[1] == None:
        if colortype == "button":
            affectedbuttoncontainer[0].config(fg_color=returnedcolor[1])
            newbutton_buttoncolor.set(returnedcolor[1])
            settingwidgets[1].config(fg_color=returnedcolor[1])
        elif colortype == "text":
            affectedbuttoncontainer[0].config(text_color=returnedcolor[1])
            newbutton_textcolor.set(returnedcolor[1])
            settingwidgets[0].config(fg_color=returnedcolor[1])
        elif colortype == "pagebg":
            if not pageID == None:
                previewboxcontainer[0].config(fg_color=returnedcolor[1])
                pagebgcolorcontainer[0].config(fg_color=returnedcolor[1])
                database.pages.update_one({'Name': pagetoedit.lower()}, {'$set': {"BackgroundColor": returnedcolor[1]}})
                if currentpage.lower() == pagetoedit.lower():
                    root.config(fg_color=returnedcolor[1])
        elif colortype == "pagefg":
            if not pageID == None:
                pagefgcolorcontainer[0].config(fg_color=returnedcolor[1])
                database.pages.update_one({'Name': pagetoedit.lower()}, {'$set': {"ForegroundColor": returnedcolor[1]}})
        else:
            pass
    root.update_idletasks()

def CreateNewItem():
    newitemuuid = randint(1, 9999999999999999)
    newitemname = "New Item"
    newitemcopynumber = 1
    existingitemnames = []
    for item in itemoptions:
        existingitemnames.append(str(item["Name"]))
    while newitemname in existingitemnames:
        newitemcopynumber += 1
        newitemname = str("New Item " + str(newitemcopynumber))
    itemtemplate = {
        "ItemID": newitemuuid,
        "Name": newitemname,
        "PriceType": "Number",
        "Price": 0.00,
        "Taxed": True,
        "ScreenGroups": [],
        "StatsGroups": [],
        "Color": "#ffffff",
        "PageLink": "none",
        "ItemLink": "none",
        "PermissionListType": "Disabled",
        "PermissionList": []
    }
    database.items.insert_one(itemtemplate)
    Draw(currentpage,True)
    ItemsMenu()
def CreateNewButton(slot):
    global currentpage
    row, column = divmod(slot-1,int(config["NetPOS"]["Columns"]))
    #1print("Row " + str(row) + " Column " + str(column))
    newbuttonid = randint(1,9999999999999999)
    buttontemplate = {
    "ButtonID": newbuttonid,
    "Text": "New Button",
    "FG": "#000000",
    "BG": "#ffffff",
    "Width": 1,
    "Height": 1,
    "Image": "",
    "Column": column,
    "Row": row,
    "Font": "OpenSans",
    "FontSize": "Normal",
    "LinkedItem": "None",
    "LinkedPage": "None",
    "LinkedScript": "None",
    "Functions":[],
}
    database.buttons.insert_one(buttontemplate)
    pageresult = database.pages.find_one({"Name": currentpage.lower()})
    pagebuttons = pageresult["Buttons"]
    pagebuttons.append(newbuttonid)
    database.pages.update_one({'Name': currentpage.lower()},{'$set':{"Buttons":pagebuttons}})
    log("Created New Button",str("Page '" + currentpage.lower() + "' Row " + str(row+1) + " Column " + str(column+1)))
    #Draw(currentpage,True)
    EditButton(newbuttonid,"Button")

def POSFunction(buttonID,em,emtype="none"):
    global buttoncommands, pageoptions, currentpage
    if em == 1:
        EditButton(buttonID,emtype)
    else:
        print("-- Running command for button #" + str(buttonID) + ":")
        starttime = time.time()
        linkedpage = database.buttons.find_one({"ButtonID": buttonID})["LinkedPage"]
        if not linkedpage == None:
            UpdatePageNames()
            if linkedpage in pageoptions:
                currentpage = linkedpage
                currentpagerawvar.set(linkedpage)
                Draw(linkedpage,False)
        endtime = time.time()
        print("-- Finished commands for button #" + str(buttonID) + " in " + str(endtime-starttime))

buttondictionary = {}

cachedbuttons = {}
cachedimages = {}

def ChangePage(trash):
    global currentpage
    currentpage = currentpagerawvar.get()
    Draw(currentpage,True)

def CacheManager(function,arg="none",arg2="none"):
    global cachedimages, cachedbuttons
    if function == "Check":
        pass
        #1print("Checking for updates in database...")
    if function == "Update":
        if arg == "all":
            #1print("Updating entire database...")
            for button in database.buttons.find():
                cachedbuttons[str(button["ButtonID"])] = button
            for image in database.images.find():
                cachedbuttons[str(button["ImageID"])] = button


CacheManager("Update","all")

#1print(cachedbuttons)

def Clear(only=None):
    global buttoncommands,buttondictionary,settingwidgets
    #Clear all widgets and buttons off the screen
    if not only == "Buttons":
        for widget in miscwidgets:
            try:
                widget.destroy()
            except:
                try:
                    widget.delete()
                except:
                    pass
        for widget in settingwidgets:
            try:
                widget.destroy()
            except:
                try:
                    widget.delete()
                except:
                    pass
    if not only == "Widgets":
        for button in buttonwidgets:
            button.place_forget()
    for widget in settingwidgets:
            try:
                widget.destroy()
            except:
                try:
                    widget.delete()
                except:
                    pass
    buttoncommands = {}
    buttondictionary = {}

pagebgcolor = "#000000"
pagefgcolor = "#ffffff"
currentpagerawvar = StringVar()
currentpagerawvar.set(currentpage)


style = ttk.Style()
style.configure("Treeview.Heading", font=('OpenSans', 24,'bold'))

itemtreeviewids = []

def ItemsMenu():
    global settingwidgets
    global itemtreeviewids
    global buttoneditorwidgets
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")
    UpdateItemNames()
    itemtreeviewids = []
    ttk.Style().configure("Treeview",rowheight=40)
    itemtreeview = ttk.Treeview(root, columns=("Name","Price","Tax","Color"), show='headings', height=10)
    itemtreeview.column("#0",width=0,stretch=NO)
    itemtreeview.column("Name",anchor="n", width=200, minwidth=200,stretch=NO)
    itemtreeview.column("Price", anchor="n", width=120, minwidth=120,stretch=NO)
    itemtreeview.column("Tax", anchor="n", width=80, minwidth=80,stretch=NO)
    itemtreeview.column("Color", anchor="n", width=200, minwidth=200,stretch=NO)
    itemtreeview.heading("#0", text="")
    itemtreeview.heading("Name", text="Name")
    itemtreeview.heading("Price", text="Price")
    itemtreeview.heading("Tax", text="Tax")
    itemtreeview.heading("Color", text="Color")
    itemtreeview.place(x=100,y=100,width=601,height=800)
    itemtreeview.bind("<<TreeviewSelect>>", ItemsMenuCallback)
    settingwidgets.append(itemtreeview)

    newitembutton = customtkinter.CTkButton(image=blankimage, font=("OpenSans",24), text_color="black", text="Create New", fg_color="#BBFFB4", width=288, height=50,
                                   command=CreateNewItem,padx=0, pady=0,
                                    justify='center')
    newitembutton.place(x=250,y=920)
    settingwidgets.append(newitembutton)
    root.update()
    tvscrollbar = customtkinter.CTkScrollbar(width=config['NetPOS']['ScrollbarThickness'],fg_color="gray",command=itemtreeview.yview)
    tvscrollbar.place(x=int(itemtreeview.winfo_x())+int(itemtreeview.winfo_width()), y=itemtreeview.winfo_y(),height=itemtreeview.winfo_height(),width=config['NetPOS']['ScrollbarThickness'])
    itemtreeview.config(yscrollcommand=tvscrollbar.set)
    settingwidgets.append(tvscrollbar)
    for item in itemoptions:
        itemtreeviewids.append(item["ItemID"])
        if item["PriceType"] == "Number":
            itemprice = "${:,.2f}".format(item["Price"])
        elif item["PriceType"] == "Percentage":
            itemprice = "{:.0%}".format(item["Price"])
        else:
            itemprice = item["Price"]
        if item["Taxed"] == True:
            itemtax = "Yes"
        else:
            itemtax = "No"

        try:
            itemcolor = hex_to_name(str(item["Color"]))
        except:
            itemcolor = item["Color"]

        itemtreeview.insert('', 'end', text=item["Name"],values=(item["Name"],str(itemprice),str(itemtax),str(itemcolor)))
    root.update()

previewboxcontainer = []
previewboxobjects = []
pagetoedit = None
def PagesMenuCallback(event):
    global pagetoedit, pagebgcolorcontainer, pagefgcolorcontainer

    try:
        pagetoedit = event.widget.get(event.widget.curselection()[0])
    except:
        pass

    if not pagetoedit == None:
        pageresult = database.pages.find_one({"Name": pagetoedit})
        previewboxcontainer[0].config(fg_color=pageresult["BackgroundColor"])
        pagefgcolorcontainer[0].config(fg_color=pageresult["ForegroundColor"])
        pagebgcolorcontainer[0].config(fg_color=pageresult["BackgroundColor"])
        namechangevar.set(pagetoedit)

def ItemsMenuCallback(event):
    print(event)
    pass



pagebgcolorcontainer = []
pagefgcolorcontainer = []


def ChangePageName():
    global currentpage, pagetoedit, pagelistcontainer
    print(namechangevar.get())
    newpagename = str(namechangevar.get()).lower().replace(" ","")
    conflicts = 0
    if newpagename == pagetoedit:
        conflicts += 1
        print("New page name has not changed!")
    elif newpagename == "":
        conflicts += 1
        print("New page name cannot be blank!")
    elif newpagename in pageoptions:
        conflicts += 1
        print("New page name already exists!")
    elif pagetoedit == "main":
        conflicts += 1
        print("Cannot edit page main")
    if conflicts == 0:
        database.pages.update_one({"Name": pagetoedit.lower()}, {"$set": {'Name': newpagename}})
        buttonslinkedtopage = database.buttons.find({"LinkedPage": pagetoedit})
        for button in buttonslinkedtopage:
            database.buttons.update_one({"ButtonID": button["ButtonID"]}, {"$set": {'LinkedPage': newpagename}})
        pagetoedit = newpagename
        if currentpage == pagetoedit:
            currentpagerawvar.set(newpagename)
            Draw(newpagename,True)
        else:
            Draw(currentpage,True)
        PagesMenu(newpagename)
    else:
        print(pagelistcontainer)
        namechangevar.set(pagetoedit)



namechangevar = StringVar()
pagelistcontainer = []

def CreateNewPage():
    UpdatePageNames()
    newpageuuid = randint(1, 9999999999999999)
    newpagename = "newpage"
    newpagecopynumber = 1
    while newpagename in pageoptions:
        newpagecopynumber += 1
        newpagename = str("newpage" + str(newpagecopynumber))
    pagetemplate = {
        "PageID": newpageuuid,
        "Name": newpagename,
        "BackgroundColor": "#87CFEC",
        "ForegroundColor": "#FFD993",
        "Buttons": [],
        "PermissionListType": "Disabled",
        "PermissionList": []
    }
    database.pages.insert_one(pagetemplate)
    Draw(currentpage,True)
    PagesMenu(newpagename)

def DeletePage():
    global currentpage, pagetoedit
    conflicts = 0
    if pagetoedit == "main":
        conflicts += 1
        print("Cannot edit page main")
    if conflicts == 0:
        database.pages.delete_one({"Name": pagetoedit.lower()})
        buttonslinkedtopage = database.buttons.find({"LinkedPage": pagetoedit.lower()})
        for button in buttonslinkedtopage:
            database.buttons.update_one({"ButtonID": button["ButtonID"]}, {"$set": {'LinkedPage': "None"}})
        if currentpage == pagetoedit:
            currentpagerawvar.set("main")
            currentpage = "main"
        Draw(currentpage, True)
        PagesMenu(currentpage)
    else:
        pass

def PagesMenu(defaultselected=None):
    global settingwidgets, pageoptions, previewboxcontainer, pagetoedit, pagebgcolorcontainer, pagefgcolorcontainer, pagelistcontainer, buttoneditorwidgets
    pagetoedit = None
    UpdatePageNames()
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")
    pagescrollbar = customtkinter.CTkScrollbar(root)
    pagelist = customtkinter.CTkListbox(root,selectmode="single",justify=CENTER,width=16,height=20,font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])),fg_color="white",text_color="black")
    pagelist.config(yscrollcommand=pagescrollbar.set)
    pagescrollbar.config(command=pagelist.yview,width=50,fg_color="gray")
    pagelist.place(x=500,y=200)
    pagelistcontainer = []
    pagelistcontainer.append(pagelist)
    root.update_idletasks()
    pagescrollbar.place(x=450,y=200,height=pagelist.winfo_height())
    for page in pageoptions:
        pagelist.insert(END,str(page))
    pagelist.bind("<<ListboxSelect>>", PagesMenuCallback)
    previewbox = Frame(width=700,height=394,highlightthickness=2,highlightbackground="black",fg_color=pagebgcolor)
    previewbox.place(x=800,y=200)
    previewtext = customtkinter.CTkLabel(text="Preview",font=("OpenSans",24))
    previewtext.place(x=800,y=200)
    pagebgcolorcontainer = []
    pagefgcolorcontainer = []
    backgroundcolortext = customtkinter.CTkLabel(text="Background Color:",text_color="black",fg_color=pagebgcolor,font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])))
    backgroundcolortext.place(x=800,y=650)
    backgroundcolorbutton = customtkinter.CTkButton(image=blankimage, fg_color="white", width=100, height=35,command=lambda ID=pagetoedit, ctype="pagebg": ColorSelectorHandler(ctype,ID))
    backgroundcolorbutton.place(x=1070,y=650)
    pagebgcolorcontainer.append(backgroundcolorbutton)

    foregroundcolorbutton = customtkinter.CTkButton(image=blankimage, fg_color="white", width=100, height=35,
                                   command=lambda ID=pagetoedit, ctype="pagefg": ColorSelectorHandler(ctype, ID))
    foregroundcolorbutton.place(x=1070, y=720)
    pagefgcolorcontainer.append(foregroundcolorbutton)

    foregroundcolortext = customtkinter.CTkLabel(text="Foreground Color:", text_color="black", fg_color=pagebgcolor, font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])))
    foregroundcolortext.place(x=805, y=720)

    pagenametext = customtkinter.CTkLabel(text="Page Name:", text_color="black", fg_color=pagebgcolor, font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])))
    pagenametext.place(x=883,y=790)

    pagenamebox = customtkinter.CTkEntry(textvariable=namechangevar,width=10,font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])))
    pagenamebox.place(x=1070,y=790)

    pagenameupdatebutton = customtkinter.CTkButton(image=blankimage, font=("OpenSans",int(config['NetPOS']['WidgetFontSize'])), text_color="black", text="Change", fg_color="#BBFFB4", width=100, height=35,
                                   command=ChangePageName,padx=0, pady=0,
                                    justify='center')
    pagenameupdatebutton.place(x=1250,y=791)

    createnewpage = customtkinter.CTkButton(image=blankimage, font=("OpenSans",24), text_color="black", text="Create New", fg_color="#BBFFB4", width=288, height=50,
                                   command=CreateNewPage,padx=0, pady=0,
                                    justify='center')
    createnewpage.place(x=450,y=980)

    deletebutton = customtkinter.CTkButton(image=blankimage, font=("OpenSans", 24), text_color="black", text="Delete", fg_color="#FF9191",
                           width=288, height=50,
                           command=DeletePage,
                           justify='center')
    deletebutton.place(x=1070, y=860)

    previewboxcontainer = []
    for object in previewboxobjects:
        object.destroy()
    previewboxcontainer.append(previewbox)
    settingwidgets.append(previewbox)
    settingwidgets.append(backgroundcolortext)
    settingwidgets.append(foregroundcolortext)
    settingwidgets.append(backgroundcolorbutton)
    settingwidgets.append(createnewpage)
    settingwidgets.append(pagenametext)
    settingwidgets.append(pagenameupdatebutton)
    settingwidgets.append(foregroundcolorbutton)
    settingwidgets.append(pagescrollbar)
    settingwidgets.append(deletebutton)
    settingwidgets.append(pagenamebox)
    settingwidgets.append(previewtext)
    settingwidgets.append(pagelist)
    pageindexer = 0
    pagelist.select_set(0)
    try:
        pagetoedit = pagelist.get(pagelist.curselection()[0])
        namechangevar.set(pagelist.get(pagelist.curselection()[0]))
    except:
        pagetoedit = None
    if not pagetoedit == None:
        pageresult = database.pages.find_one({"Name": pagetoedit})
        previewboxcontainer[0].config(fg_color=pageresult["BackgroundColor"])
        pagefgcolorcontainer[0].config(fg_color=pageresult["ForegroundColor"])
        pagebgcolorcontainer[0].config(fg_color=pageresult["BackgroundColor"])
    for pageitem in (pagelist.get(0,END)):

        if not defaultselected == None:
            if pageitem == defaultselected:
                pagelist.select_clear(0, END)
                pagelist.select_set(pageindexer)
                try:
                    pagetoedit = pagelist.get(pagelist.curselection()[0])
                    namechangevar.set(pagelist.get(pagelist.curselection()[0]))
                except:
                    pagetoedit = None
                if not pagetoedit == None:
                    pageresult = database.pages.find_one({"Name": pagetoedit})
                    previewboxcontainer[0].config(fg_color=pageresult["BackgroundColor"])
                    pagefgcolorcontainer[0].config(fg_color=pageresult["ForegroundColor"])
                    pagebgcolorcontainer[0].config(fg_color=pageresult["BackgroundColor"])
        else:
            if pageitem == currentpage:
                pagelist.select_clear(0,END)
                pagelist.select_set(pageindexer)
                try:
                    pagetoedit = pagelist.get(pagelist.curselection()[0])
                    namechangevar.set(pagelist.get(pagelist.curselection()[0]))
                except:
                    pagetoedit = None
                if not pagetoedit == None:
                    pageresult = database.pages.find_one({"Name": pagetoedit})
                    previewboxcontainer[0].config(fg_color=pageresult["BackgroundColor"])
                    pagefgcolorcontainer[0].config(fg_color=pageresult["ForegroundColor"])
                    pagebgcolorcontainer[0].config(fg_color=pageresult["BackgroundColor"])
        pageindexer += 1
def SettingsMenu():
    global buttoneditorwidgets
    global settingwidgets
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")
    downloaddatabutton = customtkinter.CTkButton(root, image=blankimage, width=300, height=50, text="Backup System Data",
                         text_color="black", fg_color="#9c9c9c",
                         command=DownloadData)
    downloaddatabutton.place(x=500,y=500)

    scriptsbutton = customtkinter.CTkButton(root, image=blankimage, width=300, height=50, text="Scripts",
                         text_color="black", fg_color="#9c9c9c",
                         command=ScriptMenu)
    scriptsbutton.place(x=500,y=700)

    uploaddatabutton = customtkinter.CTkButton(root, image=blankimage, width=300, height=50, text="Restore System Data",
                         text_color="black", fg_color="#9c9c9c",
                         command=UploadData)
    uploaddatabutton.place(x=500,y=600)

    settingwidgets.append(uploaddatabutton)
    settingwidgets.append(scriptsbutton)
    settingwidgets.append(downloaddatabutton)

def ScriptMenu():
    global buttoneditorwidgets
    global settingwidgets
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")

def DownloadData():
    global softwareversion
    destination = filedialog.askdirectory(title="Select Location")
    pages = []
    items = []
    users = []
    buttons = []
    reports = []
    statistics = []
    settings = []
    terminalsettings = []
    scripts = []
    transactionhistory = []
    logs = []
    signature = "NetPOS Database Archive"
    archivesoftwareversion = softwareversion
    archivetime = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    for page in database["pages"].find({}):
        pages.append(page)

    for item in database["items"].find({}):
        items.append(item)

    for button in database["buttons"].find({}):
        buttons.append(button)

    for user in database["users"].find({}):
        users.append(user)

    for report in database["reports"].find({}):
        reports.append(report)

    for statistic in database["statistics"].find({}):
        statistics.append(statistic)

    for setting in database["settings"].find({}):
        settings.append(setting)

    for terminalsetting in database["terminalsettings"].find({}):
        terminalsettings.append(terminalsetting)

    for script in database["scripts"].find({}):
        scripts.append(script)

    for transaction in database["transactionhistory"].find({}):
        transactionhistory.append(transaction)
    
    for log in database["logs"].find({}):
        logs.append(log)
    

    archivedictionary = {}
    archivedictionary["pages"] = pages
    archivedictionary["items"] = items
    archivedictionary["buttons"] = buttons
    archivedictionary["users"] = users
    archivedictionary["reports"] = reports
    archivedictionary["statistics"] = statistics
    archivedictionary["settings"] = settings
    archivedictionary["terminalsettings"] = terminalsettings
    archivedictionary["scripts"] = scripts
    archivedictionary["transactionhistory"] = transactionhistory
    archivedictionary["signature"] = signature
    archivedictionary["archivetime"] = archivetime
    archivedictionary["softwareversion"] = archivesoftwareversion
    
    print(archivedictionary)

    archivefile = open(os.path.join(destination, str("NetPOS Archive " + str(datetime.now().strftime("%m-%d-%Y %H-%M-%S")) + ".netarch")), "wb")
    pickle.dump(archivedictionary, archivefile)

    archivefile.close()
    messagebox.showinfo(title="NetPOS", message="Data successfully backed up!")


def UploadData():
    source = filedialog.askopenfilename(title="Select File",filetypes=[("NetPOS Data File", "*.netarch")])

    archivedatafile = open(source,"rb")

    try:
        archivedata = pickle.load(archivedatafile)
        if archivedata["signature"] == "NetPOS Database Archive":
            database["pages"].drop()
            database["buttons"].drop()
            database["items"].drop()
            database["users"].drop()
            database["reports"].drop()
            database["statistics"].drop()
            database["settings"].drop()
            database["terminalsettings"].drop()
            database["scripts"].drop()
            database["transactionhistory"].drop()
            for page in archivedata["pages"]:
                database["pages"].insert_one(page)
            for button in archivedata["buttons"]:
                database["buttons"].insert_one(button)
            for item in archivedata["items"]:
                database["items"].insert_one(item)
            for user in archivedata["users"]:
                database["users"].insert_one(user)
            for report in archivedata["reports"]:
                database["reports"].insert_one(report)
            for statistic in archivedata["statistics"]:
                database["statistics"].insert_one(statistic)
            for setting in archivedata["settings"]:
                database["settings"].insert_one(setting)
            for terminalsetting in archivedata["terminalsettings"]:
                database["terminalsettings"].insert_one(terminalsetting)
            for script in archivedata["scripts"]:
                database["scripts"].insert_one(script)
            for transaction in archivedata["transactionhistory"]:
                database["transactionhistory"].insert_one(transaction)
            messagebox.showinfo(title="NetPOS", message="Data recovery successful!")
        else:
            messagebox.showerror(title="NetPOS",message="Invalid archive file. Aborting operation.")

    except:
        messagebox.showerror(title="NetPOS",message="Invalid archive file. Aborting operation.")




def ReportsMenu():
    global buttoneditorwidgets
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")
def UsersMenu():
    global buttoneditorwidgets
    for widget in buttoneditorwidgets:
        widget.destroy()
    root.update()
    Clear("Buttons")

pageoptions = []
itemoptions = []

def UpdatePageNames():
    global pageoptions
    pageoptions = []
    for dbpage in database.pages.find({}):
        pageoptions.append(dbpage["Name"])
    pageoptions.sort()

def UpdateItemNames():
    global itemoptions
    itemoptions = []
    for dbitem in database.items.find({}):
        itemoptions.append(dbitem)
    itemoptions.sort(key=lambda x: x['Name'])

def Draw(pagename,editmode=False):
    #Draw/Redraw the screen
    global InEditMode, buttoncommands, buttondictionary, pagefgcolor, pagebgcolor, pageoptions
    #1print("Redrawing...")
    Clear()
    pageresult = database.pages.find_one({"Name":pagename.lower()})
    pagebuttons = pageresult["Buttons"]
    pagefgcolor = pageresult["ForegroundColor"]
    pagebgcolor = pageresult["BackgroundColor"]
    root.configure(fg_color=pagebgcolor)
    editmodebutton = customtkinter.CTkButton(root, image=settingsicon, width=50, height=50, text="", text_color="black", fg_color="#9c9c9c", command=ToggleEditMode)
    if editmode:
        editmodebutton.configure(image=blankimage,text="✓")
        keyboardbutton = customtkinter.CTkButton(root, image=keyboardicon, width=50, height=50, text="",
                                text_color="black", fg_color="#9c9c9c",
                                command=OpenKeyboard)
        keyboardbutton.place(x=1730, y=20)

        itemsbutton = customtkinter.CTkButton(root, image=blankimage, width=150, height=50, text="Items",
                                text_color="black", fg_color="#9c9c9c",
                                command=ItemsMenu)
        itemsbutton.place(x=700, y=20)

        pagesbutton = customtkinter.CTkButton(root, image=blankimage, width=150, height=50, text="Pages",
                                text_color="black", fg_color="#9c9c9c",
                                command=PagesMenu)
        pagesbutton.place(x=500, y=20)

        reportsbutton = customtkinter.CTkButton(root, image=blankimage, width=150, height=50, text="Reports",
                                text_color="black", fg_color="#9c9c9c",
                                command=ReportsMenu)
        reportsbutton.place(x=1100, y=20)

        settingsbutton = customtkinter.CTkButton(root, image=blankimage, width=150, height=50, text="Settings",
                             text_color="black", fg_color="#9c9c9c",
                             command=SettingsMenu)
        settingsbutton.place(x=1300, y=20)

        usersbutton = customtkinter.CTkButton(root, image=blankimage, width=150, height=50, text="Users",
                                text_color="black", fg_color="#9c9c9c",
                                command=UsersMenu)
        usersbutton.place(x=900, y=20)


        pagetext = customtkinter.CTkLabel(master=root,text="Page: ",text_color="black",fg_color=pagebgcolor,font=("OpenSans",24))
        pagetext.place(x=65,y=25)
        UpdatePageNames()
        pagedropdown = customtkinter.CTkOptionMenu(master=root, variable=currentpagerawvar, values=pageoptions, command=lambda trash=None: ChangePage(trash))
        pagedropdown.place(x=150,y=20)
        miscwidgets.append(pagedropdown)
        miscwidgets.append(pagetext)
        miscwidgets.append(itemsbutton)
        miscwidgets.append(pagesbutton)
        miscwidgets.append(settingsbutton)
        miscwidgets.append(reportsbutton)
        miscwidgets.append(keyboardbutton)
        miscwidgets.append(usersbutton)
    editmodebutton.place(x=1800,y=20)
    miscwidgets.append(editmodebutton)
    buttonconfigs = []
    invalidbuttons = []
    for button in pagebuttons:
        buttonquery = database.buttons.find_one({"ButtonID": int(button)})
        if str(buttonquery) == "None":
            #1print("Button " + str(button) + " doesn't exist. Skipping and removing from database...")
            invalidbuttons.append(int(button))
        else:
            buttonconfigs.append(database.buttons.find_one({"ButtonID": int(button)}))
    for button in invalidbuttons:
        pagebuttons.remove(int(button))
    database.pages.update_one({"Name":pagename.lower()},{"$set":{'Buttons':pagebuttons}})
    # Draw buttons on page
    #1print("Buttons on page: " + str(pagebuttons))
    occupiedcoords = []
    for button in buttonconfigs:
        #1print("drawing button")
        if button["Image"] == "":
            copiedbuttonid = 0
            copiedbuttonid += int(button["ButtonID"])
            buttoncommands[copiedbuttonid] = button["Functions"]
            print("Loading button #" + str(copiedbuttonid))
            try:
                print('FG = ' + button["FG"])
                print("BG = " + button["BG"])
                buttonwidget = customtkinter.CTkButton(master=root, width=int(int(config['NetPOS']['ButtonWidth']) + ((int(button["Width"])-1) * (int(config['NetPOS']['VerticalGap'])+int(config['NetPOS']['ButtonWidth'])))), height=int(int(config['NetPOS']['ButtonHeight']) + ((int(button["Height"])-1) * (int(config['NetPOS']['HorizontalGap'])+int(config['NetPOS']['ButtonHeight'])))), border_spacing=0, text=str(button["Text"]), text_color=button["FG"], fg_color=button["BG"], command=lambda bid=copiedbuttonid,em=editmode,emtype="Button" : POSFunction(bid,em,emtype))
                #buttonwidget = customtkinter.CTkButton(master=root,text="test", width=int(int(config['NetPOS']['ButtonWidth']) + ((int(button["Width"])-1) * (int(config['NetPOS']['VerticalGap'])+int(config['NetPOS']['ButtonWidth'])))), height=int(int(config['NetPOS']['ButtonHeight']) + ((int(button["Height"])-1) * (int(config['NetPOS']['HorizontalGap'])+int(config['NetPOS']['ButtonHeight'])))))
            except:
                buttonwidget = customtkinter.CTkButton(master=root, width=int(int(config['NetPOS']['ButtonWidth']) + ((int(button["Width"])-1) * (int(config['NetPOS']['VerticalGap'])+int(config['NetPOS']['ButtonWidth'])))), height=int(int(config['NetPOS']['ButtonHeight']) + ((int(button["Height"])-1) * (int(config['NetPOS']['HorizontalGap'])+int(config['NetPOS']['ButtonHeight'])))), text=button["Text"], command=lambda bid=copiedbuttonid,em=editmode,emtype="Button" : POSFunction(bid,em,emtype))
            print("calculating font size")
            if not str(button["FontSize"]) == str(config['NetPOS']['DefaultFontSize']):
                buttonsize = int(config['NetPOS']['DefaultFontSize'])
                buttonoptionsize = button["FontSize"]
                if buttonoptionsize == "Smaller":
                    buttonsize = int(round(buttonsize/2))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                elif buttonoptionsize == "Small":
                    buttonsize = int(round(((buttonsize/2)+buttonsize)/2))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                elif buttonoptionsize == "Smallest":
                    buttonsize = int(round(((buttonsize/3)+buttonsize)/3))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                elif buttonoptionsize == "Big":
                    buttonsize = int(round(((buttonsize * 2) + buttonsize) / 2))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                elif buttonoptionsize == "Bigger":
                    buttonsize = int(round(buttonsize * 2))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                elif buttonoptionsize == "Biggest":
                    buttonsize = int(round(buttonsize * 3))
                    buttonwidget.config(font=(button["Font"], buttonsize))
                else:
                    buttonsize = int(config['NetPOS']['DefaultFontSize'])

            else:
                pass
            print("done calculating font size")
            #buttonwidget = customtkinter.CTkButton(root, image=blankimage, width=str(int(config['NetPOS']['ButtonWidth']) + ((int(button["Width"])-1) * (int(config['NetPOS']['VerticalGap'])+int(config['NetPOS']['ButtonWidth'])))), height=str(int(config['NetPOS']['ButtonHeight']) + ((int(button["Height"])-1) * (int(config['NetPOS']['HorizontalGap'])+int(config['NetPOS']['ButtonHeight'])))), wraplength=str(int(config['NetPOS']['ButtonWidth']) + ((int(button["Width"])-1) * (int(config['NetPOS']['VerticalGap'])+int(config['NetPOS']['ButtonWidth'])))), text=button["Text"], text_color=button["FG"], fg_color=button["BG"], command=lambda bid=copiedbuttonid,em=editmode,emtype="Button" : POSFunction(bid,em,emtype))
            buttondictionary[str(copiedbuttonid)] = buttonwidget
        else:
            pass

        #Tell the screen not to draw the tiles that this button may be overlapping
        for w in range(0,int(button["Width"])):
            for h in range(0, int(button["Height"])):
               occupiedcoords.append([button["Column"]+w,button["Row"]+h])


        #root.update()
        buttonwidget.place(x=int(config["NetPOS"]["ButtonListRoot_X"])+((int(config['NetPOS']['ButtonWidth']) + int(config['NetPOS']['VerticalGap']))*button["Column"]),y=int(config["NetPOS"]["ButtonListRoot_Y"])+((int(config['NetPOS']['ButtonHeight']) + int(config['NetPOS']['HorizontalGap']))*button["Row"]))
        buttonwidgets.append(buttonwidget)
    #1print("Occupied Coords: " + str(occupiedcoords))
    emb = 0
    if editmode:
        for r in range(0,int(config["NetPOS"]["Rows"])):
            for c in range(0, int(config["NetPOS"]["Columns"])):
                root.update_idletasks()
                emb+=1
                if not [c, r] in occupiedcoords:
                    buttonwidget = customtkinter.CTkButton(root, image=blankimage, width=int(config['NetPOS']['ButtonWidth']),height=int(config['NetPOS']['ButtonHeight']), text="",text_color=config["NetPOS"]["ForegroundColor"],fg_color=pagebgcolor,command=lambda bid=emb,em=editmode,emtype="Slot" : POSFunction(bid,em,emtype))
                    buttondictionary[str(emb)] = buttonwidget
                    occupiedcoords.append([c, r])
                    buttonwidget.place(x=int(config["NetPOS"]["ButtonListRoot_X"]) + (
                            (int(config['NetPOS']['ButtonWidth']) + int(config['NetPOS']['VerticalGap'])) * c), y=int(config["NetPOS"]["ButtonListRoot_Y"]) + (
                            (int(config['NetPOS']['ButtonHeight']) + int(config['NetPOS']['HorizontalGap'])) * r))
                    buttonwidgets.append(buttonwidget)
                else:
                    #1print("Skipping the edit button located at " + str([c,r]) + " because the space is already occupied!")
                    pass
        pass
    else:
        itemlist = customtkinter.CTkListbox(bg=config['NetPOS']['ItemListBackgroundColor'],fg=config['NetPOS']['ItemListForegroundColor'],font=(config['NetPOS']['ItemListFont'],int(config['NetPOS']['ItemListFontSize'])),width=config['NetPOS']['ItemListTextLength'],height=config['NetPOS']['ItemListLines'])
        itemlist.place(x=config['NetPOS']['ItemListRoot_X'],y=config['NetPOS']['ItemListRoot_y'])
        for i in range(1, 100):
            itemlist.insert(END,"    test" + str(i))
        root.update()
        checkinfolabel = customtkinter.CTkLabel(master=root,anchor="w",fg_color=config['NetPOS']['ItemListBackgroundColor'],text_color=config['NetPOS']['ItemListForegroundColor'],font=(config['NetPOS']['ItemListFont'],int(config['NetPOS']['ItemListFontSize'])),height=1,width=int(int(config['NetPOS']['ItemListTextLength'])-8))
        checkinfolabel.place(x=int(itemlist.winfo_x()),y=int(itemlist.winfo_y())+int(itemlist.winfo_height()))
        checkinfolabel.configure(text="    testtttt")
        root.update()
        numberbuffer = customtkinter.CTkLabel(master=root,anchor="e",fg_color=config['NetPOS']['ItemListBackgroundColor'],text_color=config['NetPOS']['ItemListForegroundColor'],font=(config['NetPOS']['ItemListFont'],int(config['NetPOS']['ItemListFontSize'])),height=1,width=8)
        numberbuffer.place(x=int(itemlist.winfo_x())+int(checkinfolabel.winfo_width()),y=int(itemlist.winfo_y())+int(itemlist.winfo_height()))
        numberbuffer.configure(text="0.00    ")
        miscwidgets.append(checkinfolabel)
        miscwidgets.append(numberbuffer)
        if config['NetPOS']['ShowScrollbar'] == "Yes":
            root.update()
            itemlistscrollbar = customtkinter.CTkScrollbar(master=root,height=int(itemlist.winfo_height()+checkinfolabel.winfo_height()),width=int(config['NetPOS']['ScrollbarThickness']),fg_color="gray")
            itemlistscrollbar.place(x=int(itemlist.winfo_x())+int(itemlist.winfo_width()), y=itemlist.winfo_y())
            itemlistscrollbar.configure(command = itemlist.yview)
            itemlist.config(yscrollcommand=itemlistscrollbar.set)
            miscwidgets.append(itemlistscrollbar)
        miscwidgets.append(itemlist)
    #1print(buttondictionary)









Draw(currentpage)



#Draw(currentpage)

while True:
    root.update()
    root.update_idletasks()
