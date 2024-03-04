import gradio as gr, os,json
import xml.etree.ElementTree as ET
from tkinter import Tk, filedialog
from dddecoder import dddecoder
order=[None,'Fix','Tweaks','UI',"Scripts","Shared",'Localization','District','Campaign',"Dungeons","Monsters","Trinkets","Skin","New Class","Disable"]
Classify={
'Fix': {'bug','fix'},
'Tweaks': {'gameplay','tweaks','balance','overhaul','difficulty'},
'UI': {'ui'},
'Localization':{'localization','font'},
'District':{'district'},
'Monsters':{'monsters','enemy','boss'},
'Trinkets':{'trinket'},
'New Class':{'class','character','hero'},
'Skin':{'skin'}
}
list_data=[]
profiles=[]
Savefile_Des=""
Game_Des=""
Mods_Des=""
all_mods={}
enable_mods={}
ddd=None
dddjson=None
#############################dd_page
def on_browse(origin_data):
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    filename = filedialog.askdirectory()
    if filename:
        if os.path.isdir(filename):
            root.destroy()
            return str(filename)
        else:
            root.destroy()
            return str(filename)
    else:
        root.destroy()
        return str(origin_data)
def check_folders(Sf_Des,G_Des):
    global profiles,Savefile_Des,Game_Des
    visible = True
    if not os.path.exists(os.path.join(G_Des,"steam_appid.txt")):
        G_Des_ret=gr.update(info="範例: ..../steamapps/common/DarkestDungeon  Err: Savefile Folder Not Found!!")
        visible = False
    else:
        G_Des_ret=gr.update(info="範例: ..../steamapps/common/DarkestDungeon")
        Game_Des = G_Des
    if not os.path.exists(os.path.join(Sf_Des,"steam_init.json")):
        Sf_Des_ret=gr.update(info="範例: ..../Steam/userdata/247796443/262060/remote  Err: Game Folder Not Found!!")
        visible = False
    else:
        Sf_Des_ret=gr.update(info="範例: ..../Steam/userdata/247796443/262060/remote")
        Savefile_Des = Sf_Des
    profiles = [f for f in os.listdir(Savefile_Des) if os.path.isdir(os.path.join(Savefile_Des, f)) and f.startswith('profile_')]
    if visible:
        return (Sf_Des_ret,G_Des_ret,gr.update(visible=visible),
                gr.update(value=profiles[0],choices=profiles,interactive=True))
    else:
        return Sf_Des_ret,G_Des_ret,gr.update(visible=visible),gr.update(choices=[],interactive=True),gr.FileExplorer()
def select_profiles(index):
    global enable_mods,ddd,dddjson
    try:
        ddd=dddecoder.decode_file(os.path.join(Savefile_Des,"profile_%d\\persist.game.json"%index))
        ddd.decode()
        dddjson=ddd.data2json(ret=True)
        enable_mods=dddjson["base_root"]["applied_ugcs_1_0"]
    except:
        pass
    return gr.update(visible=True),gr.update(visible=True)
#############################mod_page
def list_to_sample():
    return [data[0:4]+data[5:] for data in list_data]
def list_rebuilder(Index, Mod_Name, Source, Folder, Type):
    global list_data
    list_data=list_data[1:]
    return {
            "%s"%Index: {
            "name": "%s"%Mod_Name,
            "source": "%s"%Source,
            "folder": "%s"%Folder,
            "Type": "%s"%Type
            }
           }
def classification_by_tag(tags_element):
    mod_Type=[]
    for tag in tags_element:
        if tag.text is not None: 
            for c,st in Classify.items():
                for s in st:
                    if s in tag.text.lower():
                        mod_Type.append(c)
    mod_Type= [data for data in sorted(mod_Type, key=lambda x: order.index(x))]
    return mod_Type[0] if len(mod_Type) else None
def classification_by_folder(folder_path):
    mod_Type=None
    folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    if "inventory"in folders:
        mod_Type= "UI"
    if "upgrades" in folders:
        mod_Type= "New Class"
    elif "campaign" in folders:
        mod_Type= "Campaign"
    elif "monsters" in folders:
        mod_Type= "Monsters"
    elif "dungeons" in folders:
        mod_Type= "Dungeons"
    elif "trinkets" in folders:
        mod_Type= "Trinkets"
    elif "heroes" in folders:
        mod_Type= "Skin"
    elif "localization" in folders:
        mod_Type= "Localization"
    elif "fonts" in folders:
        mod_Type= "Localization"
    return mod_Type
def process_json_data(enable_mods):
    global all_mods
    Workshop_Des=os.path.abspath(os.path.join(Game_Des,'..\\..\\workshop\\content\\262060'))
    Sources=(Workshop_Des,Mods_Des)
    for Des in Sources:
        for mod in os.listdir(Des):
            mod_path=os.path.join(Des, mod)
            if not os.path.isdir(mod_path): continue
            project_xml_path = os.path.join(mod_path, 'project.xml')
            if not os.path.exists(project_xml_path): continue
            tree = ET.parse(project_xml_path)
            root = tree.getroot()
            title_element = root.find('Title')
            tags_element = root.find('Tags')
            if title_element is not None:
                name = title_element.text
                mod_type=None
                if tags_element is not None:
                    mod_type=classification_by_tag(tags_element)
                if  mod_type is None: mod_type= classification_by_folder(mod_path)
                all_mods.setdefault((mod,name)[Sources.index(Des)],{
                    "name"  :name,
                    "source":("Steam","mod_local_source")[Sources.index(Des)],
                    "folder":mod_path,
                    "type":mod_type,
                })
                if mod_type == None:
                    print(name,'\n',mod_path)
    for key, data in enable_mods.items():
        if data["name"] in all_mods:
            all_mods[data["name"]].update({"index":int(key),"enable":True})
    return all_mods
def process_export_json_data(json_data):
    export_data={}
    for key, data in json_data.items():
        if data["source"] == "Steam":
            # Extract the rightmost number from the folder path and replace the name
            folder_path = data["folder"]
            rightmost_number = folder_path.split('/')[-1].split('\\')[-1]
            data["name"] = data["name"].replace(" ", rightmost_number)
        data.pop("folder")
        export_data[key]={data}
    return export_data
def Json2List(mod_data):
    result_list = []
    ll=len(enable_mods)
    disable=0
    for key, data in mod_data.items():
        if  (id := data.get("index",None)) is None:
            id = ll+disable
            disable+=1
        lst = [ id,
                os.path.join(data["folder"],"preview_icon.png"),
                data["name"],
                data["source"],
                data["folder"],
                data.get("type",None),
                data.get("enable",None)]
        result_list.append(lst)
    result_list=[data for data in sorted(result_list, key=lambda x: x[0] if x[0] is not None else ll)]
    return result_list
def export_process(json_data):
    for key, data in json_data.items():
        if data["source"] == "Steam":
            # Extract the rightmost number from the folder path and replace the name
            folder_path = data["folder"]
            rightmost_number = folder_path.split('/')[-1].split('\\')[-1]
            data["name"] = "%s"%rightmost_number
            data.pop("folder")
        elif data["source"] == "mod_local_source":
            data.pop("folder")
    return json_data
def export_list():
    global list_data
    export_dict = {}
    for data_list in list_data:
        if data_list[6]:
            export_dict[data_list[0]] = {
                "name": data_list[2],
                "source": data_list[3],
                "folder": data_list[4]
            }
    export_dict=export_process(export_dict)
    dddjson["applied_ugcs_1_0"] = export_dict
    #print(dddjson)
    ddd.load_from_dict(dddjson)
    ddd.data2json()
    ddd.encode("persist.game.json")
    #with open('output2.json', 'w',  encoding='utf8') as output_file:
    #    json.dump(export_dict, output_file, indent=4,ensure_ascii=False)
def load_mod(index):
    global list_data
    return list_data[index]
def sorted_by_type():
    global list_data
    list_data= [[idx]+data[1:] for idx,data in enumerate(sorted(list_data, key=lambda x: order.index(x[5] if x[6] else "Disable")))]
    return gr.update(samples=list_to_sample())
def update_list(index,Type):
    global list_data
    if index=='': return gr.update(samples=[data[0:4]+data[5:] for data in list_data])
    list_data[int(index)][5] = Type
    return gr.update(samples=list_to_sample())
def mod_enabled(index,enable):
    list_data[int(index)][6] = enable
    return gr.update(samples=list_to_sample())
def mod_page(index):
    global list_data,Mods_Des
    Mods_Des=os.path.abspath(os.path.join(Game_Des,'mods'))
    if True:
        mod_data = process_json_data(enable_mods)
        #print(len(mod_data))
        list_data=Json2List(mod_data)
        #print(len(list_data))
    return gr.update(samples=list_to_sample())
#############################data_page
def show_json(name):
    if name:
        try:
            ddd=dddecoder.decode_file(name)
            ddd.decode()
            return gr.update(visible=True),ddd.data2json(ret=True)
        except:
            pass
    else:
        return gr.update(visible=False),None
def data_page(index):
    return  gr.FileExplorer(
                    label=profiles[index],
                    root_dir=os.path.join(Savefile_Des, profiles[index]),
                    interactive=True
    )