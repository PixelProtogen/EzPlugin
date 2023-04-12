from tkinter import *
from os import *
from json import *
from tkinter.messagebox import *
from os import path
from re import *

from urllib.request import urlopen
import io
from base64 import b64encode
import turtle

### PRIMARY STUFF
window=Tk()
window.geometry("700x500")
window.title("EzPlugin")
window['bg']="black"

window.maxsize(700,2500)
window.minsize(700,500)

def on_ctrl_mousewheel(event): #cool thing    if event.state & 0x4:
        if event.delta > 0:
            current_size = editor_code['font'].split(' ')[-1]
            new_size = int(current_size) + 1
            editor_code.config(font=(Theme['font'], new_size))
        elif event.delta < 0:
            current_size = editor_code['font'].split(' ')[-1]
            new_size = max(1, int(current_size) - 1)
            editor_code.config(font=(Theme['font'], new_size))

def editor_launch(_func): #Code editor launcher
    global editor
    global editor_code
    
    editor = Toplevel()
    editor.title("Code Editor")
    editor.geometry("700x900")
    editor['bg']="black"
    
    editor.minsize(300,0)

    editor_code=Text(editor, bg=Theme['bg'], fg=Theme['fg'], height=40, width=64, font=Theme['font']+"  15")
    editor_code.config(insertofftime=0)
    editor_code.pack(side=LEFT, fill=BOTH, expand=YES)
    
    editor_code.bind("<KeyRelease>", lambda event: _func(editor_code))
    editor_code.bind("<Control-MouseWheel>", on_ctrl_mousewheel)

def stuff_window_launch():
    global stuff_window
    global stuff_frame_inner

    stuff_window = Toplevel()
    stuff_window.title("Selection")
    stuff_window.geometry("700x900")
    stuff_window['bg'] = "black"

    stuff_frame = Frame(stuff_window, bg=Theme['bg'])
    stuff_frame_sb = Scrollbar(stuff_frame)
    stuff_frame_sb.pack(side=RIGHT, fill=Y)

    stuff_frame_canvas = Canvas(stuff_frame, yscrollcommand=stuff_frame_sb.set, bg=Theme['bg'])
    stuff_frame_canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
    stuff_frame_sb.config(command=stuff_frame_canvas.yview)

    stuff_frame_inner = Frame(stuff_frame_canvas, bg=Theme['bg'])

    def on_mousewheel(event):
        stuff_frame_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    stuff_frame_canvas.bind_all("<MouseWheel>", on_mousewheel)

    stuff_frame_canvas.create_window((0, 0), window=stuff_frame_inner, anchor=NW)
    stuff_frame_inner.bind("<Configure>", lambda event: stuff_frame_canvas.configure(scrollregion=stuff_frame_canvas.bbox(ALL)))
    stuff_frame.pack(side=RIGHT, fill=BOTH, expand=TRUE)

targetPluginData=[None,None]
activePluginData={"Procedures":{ "Code":[] , "Text":{ "Procedures":{} , "Classes":{} } , "Build":[] },"Classes":[]}
Theme={}
config_path=r"D:/EzPlugin.config" 
prev_path=None #previous path that was opened
target_edit=None #target class/file etc to edit
global_localization_text=None
target_localization=[None,None]
##############################################################################################################################################################################
###
## MAIN FUNCTIONS
####
##############################################################################################################################################################################
def link_image(link):
    with urlopen(link) as response:
        image_data = response.read()
        return b64encode(image_data).decode()

### images
procedure_image=None
class_image=None
window_image=None
code_editor_image=None
stuff_selector_image=None
arg_text_image=None
arg_input_image=None
arg_statement_image=None
missing_image=None
###

def in_array(var,arr):
    for _var in arr:
        if _var==var:
            return True
    return False

def change_color(_text):
    line_number = 0
    line_update = 0
    while True:
        line_number += 1
        if not _text.get(f"{line_number}.0", f"{line_number}.end"): #if next line valid
            if line_update==50:
                    break
            else:
                    line_update+=1
        for tag, _None in Theme["code_editor"]["colors"].items():
            _text.tag_remove(tag, f"{line_number}.0", f"{line_number}.end") #clear all tags from line
            
        for word, color in Theme["code_editor"]["keywords"].items():
            pattern = None
            if in_array(word,{"}","{",")","(","]","[","<",">","=","!"}): 
                pattern = r'[()\[\]{}<>!=]' #bracket pattern
            else:
                pattern = r'(?i)\b{}\b'.format(escape(word)) #regular pattern

            if word == "$":
                    pattern += "|\\$"
            matches = None

            if in_array(Theme["code_editor"]["keywords"][word],{"quoted","comment"}): #quote wrap
                if Theme["code_editor"]["keywords"][word]=="quoted":
                    matches = [(m.start(), m.end()) for m in finditer(r'[\'"].+?[\'"]', _text.get(f"{line_number}.0", f"{line_number}.end"))]
                else:
                    _mid=(len(word)//2)
                    _start=word[:_mid]
                    _end=word[_mid:]
                    matches = [(m.start(), m.end()) for m in finditer(r'(?s)/{}.*?\{}'.format(_start,_end), _text.get(f"{line_number}.0", f"{line_number}.end"))]
                
            else: #regular wrap
                matches=[(m.start(), m.end()) for m in finditer(pattern, _text.get(f"{line_number}.0", END))]
                
            for start, end in matches: #adds tags
                _text.tag_add(color, f"{line_number}.{start}", f"{line_number}.{end}")
                
        for tag, color in Theme["code_editor"]["colors"].items(): #configures tags
            _text.tag_configure(tag, foreground=color)



def editor_open():
    try: 
        editor.deiconify() 
    except:
        editor_lauch(change_color)

def editor_close():
    try:
        editor.withdraw()
        print("CLOSE")
    except:
        print("already closed")

def stuff_window_open():
    try: 
        stuff_window.deiconify() 
    except:
        stuff_window_lauch(change_color)

def stuff_window_clear():
    for widget in stuff_frame_inner.winfo_children():
        widget.destroy()

def stuff_window_close():
    try:
        stuff_window_clear()
        stuff_window.withdraw()
        print("CLOSE")
    except:
        print("already closed")
#########################################################################################################################################################
def valid_object_name(_str):
    _chars = r'[.,?!{}()<>]'
    if _str == "":
        return False
    elif _str == "None":
        return False
    elif search(_chars, _str) is not None:
        return False
    elif ' ' in _str:
        return False
    else:
        return True

def write_file(file,text,fixArray):
    try:
        target=open(file,O_WRONLY,fixArray)
        rawtext=None
        data=None
        
        if (fixArray==True):
            rawtext={str(i): text[i] for i in range(len(text))}["0"]
        else:
            if (fixArray==3):
                rawtext=text
            else:
                rawtext=text
        
        if (fixArray==2 or fixArray==3):
            data=rawtext
        else:
            data=dumps(rawtext)
        
        lseek(target,0,SEEK_SET)
        truncate(file,0)
        write(target,str.encode(data))
        close(target)
        print("write finished")
    except FileNotFoundError:
        print("write error|"+file)

def read_file(file,fixArray):
    try:
         target=open(file,O_RDONLY)
         data=None
         if (fixArray==True):
             data=[loads(read(target,950150))]
         elif (fixArray==False):
             data=loads(read(target,950150))
         else:
             data=read(target,950150)
                 
             
         print("read success")
         close(target)
         return data
    except FileNotFoundError:
        print("read error")
        return "None"

def update_array(array,index,value):
    newarray=[]
    indx=-1
    for v in array:
        indx=indx+1
        if (indx==index):
            newarray.append(value)
        else:
            newarray.append(v)
    return newarray
#############################################################################################################################################################################
def Load_Images():
    global procedure_image
    global class_image
    global code_editor_image
    global window_image
    global stuff_selector_image

    global arg_text_image
    global arg_input_image
    global arg_statement_image

    global missing_image
    
    procedure_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Procedure"] ))
    class_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Class"] ))
    code_editor_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Editor"] ))
    window_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Primary"] ))
    stuff_selector_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Selection"] ))

    arg_text_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Arguments"]["Text"] ))
    arg_input_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Arguments"]["Input"] ))
    arg_statement_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Arguments"]["Statement"] ))

    missing_image=PhotoImage(data=link_image(Theme["images"]["link"]+Theme["images"]["Missing"] ))

def config_file():
    global prev_path
    global Theme
    try:
        file=open(config_path,O_RDONLY)
        data=read_file(config_path,False)

        prev_path=data[0]
        Theme=data[1]
        Load_Images()
    except FileNotFoundError:
        config=open(config_path,O_CREAT)
        data=[r"D:\EzPlugin",
              {'bg':'black','bg2':'#86c23e','fbg':'black','fg':"#efffdb",'fg2':'black','font':'Arial',"caret":"black","caret2":"white",
               "images":{
                   "link":r"https://raw.githubusercontent.com/PixelProtogen/EzPlugin/main/assets/",
                   "Class":"Class.png",
                   "Procedure":"Procedure.png",
                   "Editor":"Editor.png",
                   "Primary":"Primary.png",
                   "Selection":"Selection.png",
                   "Arguments":{
                       "Text":"arg_text.png",
                       "Input":"arg_input.png",
                       "Statement":"arg_statement.png"
                       },
                   "Missing":"missing.png"
                   },
               "code_editor":{
                   "colors":{
                       "statement":"#adffbe",
                       "brackets":"#d5e36f",
                       "quoted":"#adffed",
                       "comment":"gray",
                       "number":"#adcfff",
                       "object":"#68f760",
                       "misc":"#f79360"
                             },
                   "keywords":{
                       "if":"statement",
                       "else":"statement",
                       "return":"statement",

                       "public":"object",
                       "private":"object",
                       "void":"object",
                       "static":"object",
                       "class":"object",
                       "import":"object",
                       "new":"object",

                       "double":"number",
                       "int":"number",
                       
                       '(':"brackets",
                       ')':"brackets",
                       '{':"brackets",
                       '}':"brackets",
                       '[':"brackets",
                       ']':"brackets",
                       '<':"brackets",
                       '>':"brackets",
                       '=':"brackets",
                       "!":"brackets",

                       "$":"misc",
                       
                       '"':"quoted",
                       "'":"quoted",
                       "/**/":"comment"
                               }
                   }
               }
              ]

        prev_path=data[0]
        Theme=data[1]
        Load_Images()

        showinfo("stuff","New config file created in ({}) keep in mind that config file should be always there".format(config_path))
        
        write_file(config_path,data,False)

config_file()
##############################################################################################################################################################################
###
## TKINTER SETUP
####
##############################################################################################################################################################################
menu=Frame(width=700,height=500,bg=Theme['fbg'])

menu_label0=Label(menu,text="Path",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=2)
menu_label0.pack(pady=10)

menu_text=Text(menu, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  15",insertbackground=Theme["caret"])
menu_text.pack(pady=10)
menu_text.insert(1.0,prev_path)

menu_newfile=Button(menu,text="New Plugin",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+" 15")
menu_newfile.pack(pady=10)

menu_oldfile=Button(menu,text="Load Plugin",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+"  15")
menu_oldfile.pack(pady=10)

menu_label1=Label(menu,text="By Pixel_Protogen#2629",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=2)
menu_label1.pack(pady=10)

menu.pack()
########################################### MAIN FRAME ###########################################
main=Frame(width=700,height=500,bg=Theme['fbg'])

main_i=Button(main,text="Plugin Info",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+"  15")
main_i.pack(pady=10)

main_p=Button(main,text="Procedures",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+"  15")
main_p.pack(pady=10)

main_l=Button(main,text="Localization",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+"  15")
main_l.pack(pady=10)
########################################### PLUGIN.JSON ###########################################
plugini = Frame(width=100, height=1, bg=Theme['fbg'])

plugini_a = Button(plugini, text="Apply", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
plugini_a.grid(row=0, column=0, padx=10, pady=10)

plugini_e = Button(plugini, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
plugini_e.grid(row=0, column=1, padx=10, pady=10)
##################### PLUGIN ID
plugini_id_label = Label(plugini, text="Id", bg=Theme['bg'], fg=Theme['fg'], font=Theme['font']+"  15")
plugini_id_label.grid(row=1, column=0, padx=10, pady=10)

plugini_id_text = Text(plugini, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=20, font=Theme['font']+"  15",insertbackground=Theme["caret"])
plugini_id_text.grid(row=1, column=1, padx=10, pady=10)
##################### PLUGIN NAME
plugini_name_label = Label(plugini, text="Name", bg=Theme['bg'], fg=Theme['fg'], font=Theme['font']+"  15")
plugini_name_label.grid(row=2, column=0, padx=10, pady=10)

plugini_name_text = Text(plugini, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=20, font=Theme['font']+"  15",insertbackground=Theme["caret"])
plugini_name_text.grid(row=2, column=1, padx=10, pady=10)
##################### PLUGIN DESCRIPTION
plugini_desc_label = Label(plugini, text="Description", bg=Theme['bg'], fg=Theme['fg'], font=Theme['font']+"  15")
plugini_desc_label.grid(row=3, column=0, padx=10, pady=10)

plugini_desc_text = Text(plugini, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=20, font=Theme['font']+"  15",insertbackground=Theme["caret"])
plugini_desc_text.grid(row=3, column=1, padx=10, pady=10)
##################### PLUGIN AUTHOR
plugini_auth_label = Label(plugini, text="Author", bg=Theme['bg'], fg=Theme['fg'], font=Theme['font']+"  15")
plugini_auth_label.grid(row=4, column=0, padx=10, pady=10)

plugini_auth_text = Text(plugini, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=20, font=Theme['font']+"  15",insertbackground=Theme["caret"])
plugini_auth_text.grid(row=4, column=1, padx=10, pady=10)
##################### PLUGIN VERSION
plugini_vers_label = Label(plugini, text="Version", bg=Theme['bg'], fg=Theme['fg'], font=Theme['font']+"  15")
plugini_vers_label.grid(row=5, column=0, padx=10, pady=10)

plugini_vers_text = Text(plugini, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=20, font=Theme['font']+"  15",insertbackground=Theme["caret"])
plugini_vers_text.grid(row=5, column=1, padx=10, pady=10)
########################################### PROCEDURE CREATING ###########################################
procedureframe=Frame(width=100, height=1, bg=Theme['fbg'])

procedureframe_e = Button(procedureframe, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
procedureframe_e.pack(pady=2)

procedureframe_label0=Label(procedureframe,text="Procedures",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=2)
procedureframe_label0.pack()

procedureframe_text=Text(procedureframe, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  15",insertbackground=Theme["caret"])
procedureframe_text.pack(pady=10)

procedureframe_procedure=Button(procedureframe,text="New Procedure",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+" 15")
procedureframe_procedure.pack(pady=10)

procedureframe_class=Button(procedureframe,text="New Class",bg=Theme['bg'],fg=Theme['fg'],height=2,width=20,font=Theme['font']+" 15")
procedureframe_class.pack(pady=10)
##################### PROCEDURE EDIT
procedure_edit_frame=Frame(width=100, height=1, bg=Theme['fbg'])
class_edit_frame=Frame(width=100, height=1, bg=Theme['fbg'])
###prim
procedure_edit_frame_e = Button(procedure_edit_frame, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
procedure_edit_frame_e.grid(row=0, column=0, padx=10, pady=10)

procedure_edit_frame_a = Button(procedure_edit_frame, text="Save", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
procedure_edit_frame_a.grid(row=0, column=1, padx=10, pady=10)
#prim
procedure_edit_frame_label0=Label(procedure_edit_frame,text="?",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=0)
procedure_edit_frame_label0.grid(row=1, column=0, padx=10, pady=10)

procedure_edit_frame_label_t=Label(procedure_edit_frame,text="Procedure",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=0)
procedure_edit_frame_label_t.grid(row=1, column=1, padx=10, pady=10)
#color
procedure_edit_frame_label1=Label(procedure_edit_frame,text="Color",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label1.grid(row=2, column=0, padx=10, pady=10)

procedure_edit_frame_clr=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_clr.grid(row=2, column=1, padx=10, pady=10)

#inline
procedure_edit_frame_label2=Label(procedure_edit_frame,text="Inline",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label2.grid(row=3, column=0, padx=10, pady=10)

procedure_edit_frame_inline = Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_inline.grid(row=3, column=1, padx=10, pady=10)

#output
procedure_edit_frame_label4=Label(procedure_edit_frame,text="Output",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label4.grid(row=4, column=0, padx=10, pady=10)

procedure_edit_frame_text_out=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_text_out.grid(row=4, column=1, padx=10, pady=10)

#prevStatement
procedure_edit_frame_label5=Label(procedure_edit_frame,text="Prev Statement",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label5.grid(row=5, column=0, padx=10, pady=10)

procedure_edit_frame_text_prevs=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_text_prevs.grid(row=5, column=1, padx=10, pady=10)

#nextStatement
procedure_edit_frame_label6=Label(procedure_edit_frame,text="Next Statement",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label6.grid(row=6, column=0, padx=10, pady=10)

procedure_edit_frame_text_nexts=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_text_nexts.grid(row=6, column=1, padx=10, pady=10)

##root
procedure_edit_frame_label7=Label(procedure_edit_frame,text="toolbox [Class]",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=0)
procedure_edit_frame_label7.grid(row=7, column=0, padx=10, pady=10)

procedure_edit_frame_text_tb=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=0, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_text_tb.grid(row=7, column=1, padx=10, pady=10)

###args
procedure_edit_frame_arg = Button(procedure_edit_frame, text="New Argument", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
procedure_edit_frame_arg.grid(row=8, column=0, padx=10, pady=10)

procedure_edit_frame_text_arg=Text(procedure_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
procedure_edit_frame_text_arg.grid(row=8, column=1, padx=10, pady=10)

#rem

procedure_edit_frame_r = Button(procedure_edit_frame, text="Remove Procedure", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
procedure_edit_frame_r.grid(row=9, column=0, padx=10, pady=10)

#########################
class_edit_frame_e = Button(class_edit_frame, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
class_edit_frame_e.grid(row=0, column=0, padx=10, pady=10)

class_edit_frame_a = Button(class_edit_frame, text="Save", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
class_edit_frame_a.grid(row=0, column=1, padx=10, pady=10)
#prim
class_edit_frame_label0=Label(class_edit_frame,text="?",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=2)
class_edit_frame_label0.grid(row=1, column=0, padx=10, pady=10)

class_edit_frame_label_t=Label(class_edit_frame,text="Class",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  15",height=2)
class_edit_frame_label_t.grid(row=1, column=1, padx=10, pady=10)
#color
class_edit_frame_label1=Label(class_edit_frame,text="color",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
class_edit_frame_label1.grid(row=2, column=0, padx=10, pady=10)

class_edit_frame_text_clr=Text(class_edit_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
class_edit_frame_text_clr.grid(row=2, column=1, padx=10, pady=10)
#api
class_edit_frame_label2=Label(class_edit_frame,text="Is Api Type",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
class_edit_frame_label2.grid(row=3, column=0, padx=10, pady=10)

class_edit_frame_api = Button(class_edit_frame, text="False", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
class_edit_frame_api.grid(row=3, column=1, padx=10, pady=10)
#rem
class_edit_frame_r = Button(class_edit_frame, text="Remove Class", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
class_edit_frame_r.grid(row=4, column=1, padx=10, pady=10)
##################### PROCEDURE ARGUMENT
arg_frame=Frame(width=100, height=1, bg=Theme['fbg'])

arg_frame_e = Button(arg_frame, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
arg_frame_e.grid(row=0, column=0, padx=10, pady=10)

arg_frame_a = Button(arg_frame, text="Save", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
arg_frame_a.grid(row=0, column=1, padx=10, pady=10)
#type

arg_frame_label0=Label(arg_frame,text="Type",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
arg_frame_label0.grid(row=1, column=0, padx=10, pady=10)

arg_frame_type=Text(arg_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
arg_frame_type.grid(row=1, column=1, padx=10, pady=10)

#name

arg_frame_label1=Label(arg_frame,text="Name",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
arg_frame_label1.grid(row=2, column=0, padx=10, pady=10)

arg_frame_name=Text(arg_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
arg_frame_name.grid(row=2, column=1, padx=10, pady=10)

#check

arg_frame_label2=Label(arg_frame,text="Check",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
arg_frame_label2.grid(row=3, column=0, padx=10, pady=10)

arg_frame_chec=Text(arg_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
arg_frame_chec.grid(row=3, column=1, padx=10, pady=10)

#rem

arg_frame_r = Button(arg_frame, text="Remove Argument", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
arg_frame_r.grid(row=4, column=1, padx=10, pady=10)
##################### LOCALIZATION
lang_frame=Frame(width=100, height=1, bg=Theme['fbg'])

lang_frame_e = Button(lang_frame, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
lang_frame_e.grid(row=0, column=0, padx=10, pady=10)
### block localization
lang_txt_frame=Frame(width=100, height=1, bg=Theme['fbg'])

lang_txt_frame_e = Button(lang_txt_frame, text="Exit", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
lang_txt_frame_e.grid(row=0, column=0, padx=10, pady=10)

lang_txt_frame_label0=Label(lang_txt_frame,text="?",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
lang_txt_frame_label0.grid(row=0, column=1, padx=10, pady=10)
###text
lang_txt_frame_label1=Label(lang_txt_frame,text="Display Text",bg=Theme['bg'],fg=Theme['fg'],font=Theme['font']+"  13",height=2)
lang_txt_frame_label1.grid(row=1, column=0, padx=10, pady=10)

lang_txt_frame_txt=Text(lang_txt_frame, bg=Theme['bg2'], fg=Theme['fg2'], height=2, width=60, font=Theme['font']+"  10",insertbackground=Theme["caret"])
lang_txt_frame_txt.grid(row=1, column=1, padx=10, pady=10)
##apply

lang_txt_frame_a = Button(lang_txt_frame, text="Save", bg=Theme['bg'], fg=Theme['fg'], height=2, width=20, font=Theme['font']+"  15")
lang_txt_frame_a.grid(row=2, column=0, padx=10, pady=10)
##############################################################################################################################################################################
###
## EXTRA FUNCTIONS
####
##############################################################################################################################################################################
def exists(path):
    try:
        file=open(path,O_RDONLY)
        close(file)
        return True
    except FileNotFoundError:
        return False

def basename(path):
    return path.split(r'/',-1)[-1].split(".",-1)[0]

def clamp(x,_max,_min):
    if x<_min:
        return _min
    else:
        if x>_max:
            return _max
        else:
            return x

def bool_str(obj):
    if obj==True:
        return "True"
    else:
        if obj==False:
            return "False"
        else:
            if obj=="True" or obj=="true":
                return True
            else:
                if obj=="False" or obj=="false":
                    return False
                else:
                        return obj

def check(table,txt,value):
   if len(table)>0:
            if table.get(txt):
                    return table[txt]
            else:
                    return value
   else:
           return value

def find_arg(args,_name):
    pos=-1
    for arg in args:
        pos=pos+1
        if arg["name"]==_name:
            return pos
    return None
##############################################################################################################################################################################
###
## PROCEDURE MAKER
####
##############################################################################################################################################################################
procedure_data={
    "mcreator_field":{
        "input_value":"inputs",
        #"field_dropdown":"fields",
        "field_input":"fields",
        "input_statement":"statements"
        }

    }

def format_val(_value):
        if _value == 'true' or _value == 'True':
                return True
        elif _value == 'false' or _value == 'False':
                return False
        elif _value == 'null':
                return None
        elif valid_object_name(_value)==False:
                return "_/skip"
        else:
                return _value

def format_values(array):
    arr = {}
    for _value_name, _value in array.items():
            _value=format_val(_value)
            if _value != "_/skip":
                    arr[_value_name] = _value
    print(arr)
    return arr


def new_arg_data(_type,_name,_check):
    arg={"type":_type,"name":_name}
    if _check is not None and _check != "_/skip":
        arg["check"]=_check
    return arg

_arg_data=[]
def arg_frame_ui(_args,_name):
    global _arg_data
    
    stuff_window_close()
    target_pos=find_arg(_args,_name)
    target_arg=_args[target_pos]
    
    procedure_edit_frame.pack_forget()
    editor_close()
    arg_frame.pack()

    _arg_data=[target_pos,_args]
    
    arg_frame_name.delete(1.0, END)
    arg_frame_type.delete(1.0, END)
    arg_frame_chec.delete(1.0, END)

    arg_frame_name.insert(1.0, target_arg["name"])
    arg_frame_type.insert(1.0, target_arg["type"])
    arg_frame_chec.insert(1.0, check(target_arg,"check","None") )

def apply_arg():
    _new_arg_data=_arg_data
    data=read_file(target_edit,True)
    
    _new_name=arg_frame_name.get(1.0,END).replace('\n', '')
    _new_type=arg_frame_type.get(1.0,END).replace('\n', '')
    _new_chec=format_val( arg_frame_chec.get(1.0,END).replace('\n', '') )
    
    _new_arg_data[1][ _new_arg_data[0] ]=new_arg_data(_new_type,_new_name,_new_chec)
    data[0]["args0"]=_new_arg_data[1]
    write_file(target_edit,data,True)
    
def remove_arg():
    _new_arg_data=_arg_data
    data=read_file(target_edit,True)
    del _new_arg_data[1][ _new_arg_data[0] ]
    data[0]["args0"]=_new_arg_data[1]
    write_file(target_edit,data,True)
    open_edit_ui(basename(target_edit)+".json",False)

def load_args(array, frame):
    print("ARGS")
    for value in array:
        _image_type_arg={"input_value":arg_input_image,"field_input":arg_text_image,"input_statement":arg_statement_image,"unknown":missing_image}
        button_frame=Canvas(frame,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_frame.pack(side=TOP)

        button_image=Canvas(button_frame,width=50,height=50,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_image.pack(side=LEFT)
        
        button = Button(button_frame, text="{} ({})".format(value["name"],value["type"]), bg=Theme['bg'], fg=Theme['fg'], font=Theme['font'])
        button.pack(side=RIGHT)

        arg_iamge=check(_image_type_arg,value["type"],_image_type_arg["unknown"])
        
        button_image.create_image(0, 0, anchor=NW, image=arg_iamge)
        button["command"]=lambda _value=value["name"],_args=array: arg_frame_ui(_args,_value)
                

def procedure_json():
    _data=read_file(target_edit,True)
    data=[{}]
    data[0]["args0"]=_data[0]["args0"]
    toFormat={}

    data[0]["colour"]=clamp( int( procedure_edit_frame_clr.get(1.0,END) ) , 360 , 1 )
    _args=data[0]["args0"]
    
    toFormat["inputsInline"]=procedure_edit_frame_inline.get(1.0,END).replace('\n', '')
    toFormat["previousStatement"]=procedure_edit_frame_text_prevs.get(1.0,END).replace('\n', '')
    toFormat["nextStatement"]=procedure_edit_frame_text_nexts.get(1.0,END).replace('\n', '')
    toFormat["output"]=procedure_edit_frame_text_out.get(1.0,END).replace('\n', '')
    
    data[0]["mcreator"]={"toolbox_id":procedure_edit_frame_text_tb.get(1.0,END).replace('\n', '')}
    load_args(_args,stuff_frame_inner)
    
    for _type,_var in  format_values(toFormat).items():
            data[0][_type]=_var
    for _type,_var in args_to_stuff(_args).items(): #load additional stuff
        data[0]["mcreator"][_type]=_var
    
    write_file(target_edit,data,True)

def new_arg(file,arg):
    data=read_file(file,True)
    data[0]["args0"].append(arg)
    write_file(file,data,True)
    procedure_json()

def _new_arg():
    new_arg( target_edit , new_arg_data("input_value",procedure_edit_frame_text_arg.get(1.0,END).replace('\n', ''),None) )
                
def args_to_stuff(arg_array): #makes mcreator stuff from args0
    output={}
    for arg in arg_array:
        arg_type=procedure_data["mcreator_field"][ arg['type'] ]
        if arg_type=="inputs":
            output["inputs"]=check(output,"inputs",[])
            output["inputs"].append(arg["name"])
        else:
            if arg_type=="fields":
                output["fields"]=check(output,"fields",[])
                output["fields"].append(arg["name"])
            else:
                if arg_type=="statements":
                    output["statements"]=check(output,"statements",[])
                    output["statements"].append({"name":arg["name"]})
    return output
##############################################################################################################################################################################
###
## INTERACTIONS
####
##############################################################################################################################################################################
def procedure_exists(_name,_class):
        #Build
        
        if _class=="Classes":
                for _data in activePluginData["Classes"]:
                        print(_data[0])
                        if _data[0]==_name:
                                return True
                return True
        elif _class=="Procedures":
                for _data in activePluginData["Procedures"]["Build"]:
                        if _data[0]==_name:
                                return True
                return True

def save_localization_data(_new):
        global global_localization_text
        _in={"Procedures":"blockly.block.","Classes":"blockly.category."}
        final=""
        for _type,_data in _new.items():
                for _block,_text in _data.items():
                        if exists(targetPluginData[0]+r'procedures/'+_block+'.json'):
                                FixedBlock=_block.replace('$', '')
                                final=final+_in[_type]+FixedBlock+"="+_text+"\n"
        global_localization_text=final.encode()
        write_file(targetPluginData[0]+r"/lang/texts.properties",final,3)

def localization_array_touse():
        data=global_localization_text.decode()
        final={}
        for _text in data.split("\n"):
                raw=_text.split("=")
                raw2=raw[0].split(".")
                _object_text="=".join(raw[1:])
                _type=None
                if raw[0]!='':
                        if raw2[-2]=="category":
                                _type="Classes"
                        elif raw2[-2]=="block":
                                _type="Procedures"
                        final[raw2[-1]]=[_type,_object_text]
        print(data)
        return final

def apply_localization():
        TXT=lang_txt_frame_txt.get(1.0,END).replace('\n', '')
        activePluginData["Procedures"]["Text"][target_localization[0]][target_localization[1]]=TXT
        save_localization_data(activePluginData["Procedures"]["Text"])

def apply_class():
    data=read_file(target_edit,True)
    data[0]["color"]=clamp( int( class_edit_frame_text_clr.get(1.0,END).replace('\n', '') ) , 360 , 1 )
    data[0]["api"]=bool_str( class_edit_frame_api["text"] )
    write_file(target_edit,data,True)

def apply_procedure():
    stuff_window_clear()
    procedure_json()
    data_code=editor_code.get("1.0",END)
    write_file( (targetPluginData[1]+r'Procedures/'+ basename(target_edit)+".java.ftl"), data_code , 3 )
    
def open_edit_ui(_name,isClass):
    global target_edit
    stuff_window_clear()
    if isClass==True:
        procedureframe.pack_forget()
        class_edit_frame.pack()
        stuff_window_close()
        target_edit=targetPluginData[0]+r'procedures/'+_name
        #
        data=read_file(target_edit,True)
        #
        class_edit_frame_text_clr.delete(1.0, END)
        class_edit_frame_api["text"]=bool_str(data[0]["api"])
        class_edit_frame_text_clr.insert(1.0, data[0]["color"])
        class_edit_frame_label0['text']=_name
    else:
        procedureframe.pack_forget()
        arg_frame.pack_forget()
        procedure_edit_frame.pack()
        target_edit=targetPluginData[0]+r'procedures/'+_name
        #
        data=read_file(target_edit,True)
        editor_open()
        #
        editor_code.delete(1.0,END)
        procedure_edit_frame_clr.delete(1.0, END)
        procedure_edit_frame_inline.delete(1.0,END)
        procedure_edit_frame_text_prevs.delete(1.0,END)
        procedure_edit_frame_text_nexts.delete(1.0,END)
        procedure_edit_frame_text_out.delete(1.0,END)
        procedure_edit_frame_text_tb.delete(1.0,END)

        inline_text="True"
        if data[0]["inputsInline"]==True:
                inline_text="True"
        elif data[0]["inputsInline"]==False:
                inline_text="False"
        elif data[0]["inputsInline"] is not None:
                inline_text=data[0]["inputsInline"]

        editor_code.insert(1.0,read_file( (targetPluginData[1]+r'Procedures/'+ basename(target_edit)+".java.ftl") , 3 ) )
        procedure_edit_frame_clr.insert(1.0,data[0]["colour"])
        procedure_edit_frame_inline.insert(1.0,inline_text )
        procedure_edit_frame_text_prevs.insert(1.0,check(data[0],"previousStatement","null") )
        procedure_edit_frame_text_nexts.insert(1.0,check(data[0],"nextStatement","null") )
        procedure_edit_frame_text_tb.insert(1.0,check(data[0]["mcreator"],"toolbox_id","None") )
        procedure_edit_frame_text_out.insert(1.0,check(data[0],"output","None") )
        #
        change_color(editor_code)
        procedure_edit_frame_label0['text']=_name
        stuff_window_open()
        procedure_json()

def create_procedure_buttons(array, frame, addtxt,isClass):
    global _cb_row
    save_localization_data(activePluginData["Procedures"]["Text"])
    for value in array:
        button_frame=Canvas(frame,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_frame.pack(side=TOP)

        button_image=Canvas(button_frame,width=50,height=50,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_image.pack(side=LEFT)
        
        button = Button(button_frame, text=value, bg=Theme['bg'], fg=Theme['fg'], font=Theme['font'])
        button.pack(side=RIGHT)
        
        if isClass==True:
            button_image.create_image(0, 0, anchor=NW, image=class_image)
            button["command"]=lambda _value=value: open_edit_ui(_value,True)
        else:
            button_image.create_image(0, 0, anchor=NW, image=procedure_image)
            button["command"]=lambda _value=value: open_edit_ui(_value,False)

def load_APD():
    global activePluginData
    files=listdir(targetPluginData[0]+r'/procedures')
    activePluginData={"Procedures":{ "Code":[] , "Text":{ "Procedures":{} , "Classes":{} } , "Build":[] },"Classes":[]}

    for _file,_data in localization_array_touse().items():
            activePluginData["Procedures"]["Text"][_data[0] ][_file]=_data[1]
    print(activePluginData)
            
    for file in files:
        if basename(file).startswith("$"):
            activePluginData["Classes"].append(file)
        else:
            activePluginData["Procedures"]["Build"].append(file)
            activePluginData["Procedures"]["Code"].append(targetPluginData[1]+r'Procedures/'+ basename(file).replace('.json', '.java.ftl'))

def update_procedures():
    global _cb_row
    _cb_row=-1
    load_APD()

    stuff_window_clear()
    stuff_window_open()
    
    create_procedure_buttons(activePluginData["Procedures"]["Build"],stuff_frame_inner," (Procedure)",False)
    create_procedure_buttons(activePluginData["Classes"],stuff_frame_inner," (Class)",True)
###PROCEDURE FILES
    
def new_procedure_file(name):
    PATH0=targetPluginData[0]+r'procedures/'+name+'.json'
    PATH1=targetPluginData[1]+r'procedures/'+name+'.java.ftl'
    if exists(PATH0):
        showinfo('error','Procedure Already Exists')
    else:
        fileA=open(PATH0,O_CREAT)
        fileB=open(PATH1,O_CREAT)
        close(fileA)
        close(fileB)
        Basic=[{"args0":[], "colour":1 , "mcreator":{ "toolbox_id":"none" } }]
        write_file(PATH0,Basic,True)
        write_file(PATH1,"#stuff",3)
        update_procedures()
        
    return [PATH0,PATH1]

def new_class_file(name):
    PATH0=targetPluginData[0]+r'procedures/$'+name+'.json'
    if exists(PATH0):
        showinfo('error','Class Already Exists')
    else:
        fileA=open(PATH0,O_CREAT)
        close(fileA)
        Basic=[{"color":1,"api":False}]
        write_file(PATH0,Basic,True)
        update_procedures()
        
    return [PATH0]
#REM
def rem_procedure_file(name):
    PATH0=targetPluginData[0]+r'procedures/'+name+'.json'
    PATH1=targetPluginData[1]+r'procedures/'+name+'.java.ftl'
    if exists(PATH0):
        remove(PATH0)
        remove(PATH1)
        update_procedures()
    else:
        showinfo('error','Procedure Doesnt Exists')

def remove_procedure():
        rem_procedure_file(basename(target_edit))
        procedures_UI()

def _remove_class(name):
        PATH0=targetPluginData[0]+r'procedures/'+name+'.json'
        if exists(PATH0):
                remove(PATH0)
                update_procedures()
        else:
                showinfo('error','unable to delete class')

def remove_class():
        _remove_class(basename(target_edit))
        procedures_UI()
# DEF
def _new_procedure_file():
        _name=procedureframe_text.get(1.0,END).replace('\n', '')
        if valid_object_name(_name)==True:
                new_procedure_file(_name)
        else:
                showinfo('error','procedure name should not include special chars or spaces')

def _new_class_file():
    new_class_file(procedureframe_text.get(1.0,END).replace('\n', ''))
###CONFIGURATION UPDATE
def update_config():
    pluginjsonstart=read_file(targetPluginData[0]+r'plugin.json',True)
    pluginjsonstart[0]["id"]=plugini_id_text.get(1.0,END).replace('\n', '')
    pluginjsonstart[0]["info"]["name"]=plugini_name_text.get(1.0,END).replace('\n', '')
    pluginjsonstart[0]["info"]["description"]=plugini_desc_text.get(1.0,END).replace('\n', '')
    pluginjsonstart[0]["info"]["author"]=plugini_auth_text.get(1.0,END).replace('\n', '')
    pluginjsonstart[0]["info"]["version"]=plugini_vers_text.get(1.0,END).replace('\n', '')

    print(pluginjsonstart[0])
    write_file(targetPluginData[0]+r'plugin.json',pluginjsonstart,True)

def main_UI():
    menu.pack_forget()
    lang_frame.pack_forget()
    plugini.pack_forget()
    procedureframe.pack_forget()
    stuff_window_close()
    main.pack()
    window['bg']=main['bg']

def lang_txt_UI(_name,Class):
        global target_localization
        lang_frame.pack_forget()
        lang_txt_frame.pack()
        stuff_window_close()
        lang_txt_frame_label0["text"]=_name

        lang_txt_frame_txt.delete(1.0,END)
        print(activePluginData["Procedures"]["Text"][Class])
        lang_txt_frame_txt.insert(1.0,check(activePluginData["Procedures"]["Text"][Class],tuple([basename(_name)]),"stuff")) 
        target_localization=[Class,basename(_name)]

def create_lan_procedure_buttons(array, frame, addtxt,isClass):
    global _cb_row
    for value in array:
        button_frame=Canvas(frame,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_frame.pack(side=TOP)

        button_image=Canvas(button_frame,width=50,height=50,bg=Theme["bg"],borderwidth=0,highlightthickness=0)
        button_image.pack(side=LEFT)
        
        button = Button(button_frame, text=value, bg=Theme['bg'], fg=Theme['fg'], font=Theme['font'])
        button.pack(side=RIGHT)
        
        if isClass==True:
            button_image.create_image(0, 0, anchor=NW, image=class_image)
            button["command"]=lambda _value=value: lang_txt_UI(_value,"Classes")
        else:
            button_image.create_image(0, 0, anchor=NW, image=procedure_image)
            button["command"]=lambda _value=value: lang_txt_UI(_value,"Procedures")

def lang_UI():
        main.pack_forget()
        lang_txt_frame.pack_forget()
        lang_frame.pack()
        stuff_window_open()
        load_APD()
        
        create_lan_procedure_buttons(activePluginData["Procedures"]["Build"],stuff_frame_inner," (Procedure)",False)
        create_lan_procedure_buttons(activePluginData["Classes"],stuff_frame_inner," (Class)",True)

def procedures_UI():
    procedure_edit_frame.pack_forget()
    class_edit_frame.pack_forget()
    main.pack_forget()
    procedureframe.pack()
    editor_close()
    update_procedures()

def plugin_info():
    pluginjsonstart=read_file(targetPluginData[0]+r'plugin.json',True)
    main.pack_forget()
    plugini.pack()
    window['bg']=plugini['bg']
    
    plugini_id_text.delete(1.0, END)
    plugini_name_text.delete(1.0, END)
    plugini_desc_text.delete(1.0, END)
    plugini_auth_text.delete(1.0, END)
    plugini_vers_text.delete(1.0, END)
    
    plugini_id_text.insert(1.0, pluginjsonstart[0]["id"])
    plugini_name_text.insert(1.0,pluginjsonstart[0]["info"]["name"])
    plugini_desc_text.insert(1.0,pluginjsonstart[0]["info"]["description"])
    plugini_auth_text.insert(1.0,pluginjsonstart[0]["info"]["author"])
    plugini_vers_text.insert(1.0,pluginjsonstart[0]["info"]["version"])

##############################################################################################################################################################################
###
## LOAD
####
##############################################################################################################################################################################
def plugin_interact(path,version,read_only):
    fullpath=path+r"/"
    try:
        if (read_only==True):
            file=open(fullpath+r'plugin.json',O_RDONLY)
            global targetPluginData
            global global_localization_text
            targetPluginData=[fullpath,fullpath+r"forge-"+version+r'/']
            close(file)
            write_file(config_path, update_array(read_file(config_path,False),0,path),False )

            LD=fullpath+r"/lang/texts.properties"
            print(LD)
            localization_data=read_file(LD,3)
            global_localization_text=localization_data
            #convert_localization_data(localization_data,False)
            
            main_UI()
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        if (read_only==False):
            try:
                file=open(fullpath+r'plugin.json',O_RDONLY)
                close(file)
                showinfo('error','Plugin folder already exist')
            except:
                            print("new file")
                            mkdir(fullpath)
                            mkdir(fullpath+r"/procedures")
                            mkdir(fullpath+r"/lang")
                            mkdir(fullpath+r"forge-"+version)
                            mkdir(fullpath+r"forge-"+version+r"/procedures")
                            
                            fileA=open(fullpath+r"/lang/texts.properties",O_CREAT)
                            fileB=open(fullpath+r'plugin.json',O_CREAT)

                            pluginjsonstart=[{"id":"testid",
                                              "minversion": 202300108712,
                                              "maxversion": 202300199999,
                                              "info":{
                                                  "name":"pluginname",
                                                  "description":"description",
                                                  "author":"you",
                                                  "version":"0.0.1"
                                                  }
                                              }]

                            plugini_id_text.insert(1.0,"testid")
                            plugini_name_text.insert(1.0,"pluginname")
                            plugini_desc_text.insert(1.0,"description")
                            plugini_auth_text.insert(1.0,"you")
                            plugini_vers_text.insert(1.0,"0.0.1")

                            write_file(fullpath+r'plugin.json',pluginjsonstart,True)

                            print(read_file(fullpath+r'plugin.json',True))
                            targetPluginData=[fullpath,fullpath+r"forge-"+version+r'/']

                            close(fileA)
                            close(fileB)
            
                            main_UI()
        else:
            showinfo('error','couldnt find plugin folder')

def old_file():
    TXT=menu_text.get(1.0,END).replace('\n', '')
    print("existing")
    plugin_interact(r''+TXT,"1.19.2",True)


def new_file():
    TXT=menu_text.get(1.0,END).replace('\n', '')
    plugin_interact(r''+TXT,"1.19.2",False)

def boolean_button(button):
    if bool_str(button["text"])==True:
        button["text"]="False"
    else:
        button["text"]="True"

##############################################################################################################################################################################
###
## STARTUP
####
##############################################################################################################################################################################
    
# bind functions
menu_newfile["command"]=new_file
menu_oldfile["command"]=old_file
plugini_a["command"]=update_config

main_i["command"]=plugin_info
main_p["command"]=procedures_UI
main_l["command"]=lang_UI

plugini_e["command"]=main_UI
procedureframe_e["command"]=main_UI
lang_frame_e["command"]=main_UI

procedure_edit_frame_e["command"]=procedures_UI
class_edit_frame_e["command"]=procedures_UI

lang_txt_frame_e["command"]=lang_UI

class_edit_frame_a["command"]=apply_class
procedure_edit_frame_a["command"]=apply_procedure
arg_frame_a["command"]=apply_arg
lang_txt_frame_a["command"]=apply_localization

arg_frame_e["command"]= lambda: open_edit_ui(basename(target_edit)+".json",False)

procedureframe_procedure["command"]=_new_procedure_file
procedureframe_class["command"]=_new_class_file
procedure_edit_frame_arg["command"]=_new_arg

class_edit_frame_api["command"]= lambda: boolean_button(class_edit_frame_api)

arg_frame_r["command"]=remove_arg
procedure_edit_frame_r["command"]=remove_procedure
class_edit_frame_r["command"]=remove_class
# start
editor_launch(change_color)
stuff_window_launch()
stuff_window_close()
editor_close()

editor_code["insertbackground"]=Theme["caret2"] 
editor['bg']=Theme['bg']
window['bg']=Theme['bg']
stuff_window['bg']=Theme['bg']

editor.iconphoto(False,code_editor_image)
window.iconphoto(False,window_image)
stuff_window.iconphoto(False,stuff_selector_image)

window.mainloop()
