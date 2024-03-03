import gradio as gr
import os
import json
import sys
import winreg
from gradio_fun import fun as grfun

def gradio_init():
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0].replace('/', '\\')
    except:
        steam_path = None
    with gr.Blocks() as demo:
        with gr.Tab("Darkest Dungeon路徑"):
            with gr.Column():
                with gr.Row():
                    with gr.Column(scale=4):
                        Savefile_Des = gr.Textbox(label="Select Save File Folder", interactive=False,
                        value=os.path.join(steam_path,"userdata\\247796443\\262060\\remote") if steam_path else None,
                        info="範例: ..../Steam/userdata/247796443/262060/remote")
                    with gr.Column(scale=1):
                        Savefile_Des_btn = gr.Button("Browse", min_width=100)
                with gr.Row():
                    with gr.Column(scale=4):
                        Game_Des = gr.Textbox(label="Select Game Folder", interactive=False,
                        value=os.path.join(steam_path,"steamapps\\common\\DarkestDungeon") if steam_path else None,
                        info="範例: ..../steamapps/common/DarkestDungeon")
                    with gr.Column(scale=1):
                        Game_Des_btn = gr.Button("Browse", min_width=100)
                with gr.Row():
                    Check_btn = gr.Button("Check Game Saves",variant='primary', min_width=100)
                with gr.Row(visible=False) as profile_page:
                    profile_drop = gr.Dropdown(choices=[], label="profile", info="選擇存檔",type='index',allow_custom_value=True)
        with gr.Tab("模組管理",visible=False) as mod_page:
            with gr.Column():
                Export = gr.Button(value="Export Data")
                Sort = gr.Button(value="自動排序")
            with gr.Row():
                with gr.Column(scale=1):
                    Image   =gr.Image(type="filepath",height=200,width=200,interactive=False,label="Icon")
                with gr.Column(scale=5):
                    Mod_Name=gr.Textbox("", interactive=False,label="Mod Name")
                    Folder  =gr.Textbox("", interactive=False,label="Folder")
            Index   =gr.Textbox("", interactive=False,label="Index")
            Source  =gr.Textbox("", interactive=False,label="Source")
            Type    =gr.Dropdown(grfun.order, label="Type", info="選擇種類以排序")
            Enable  =gr.Checkbox(label="Enable", info="啟用")
            examples = gr.Dataset(samples=[], components=[Index,Image,Mod_Name,Source,Type,Enable], type="index",samples_per_page=300)
        with gr.Tab("資料管理",visible=False) as data_page:
            with gr.Row():
                with gr.Column(scale=1):
                    FileEpr = gr.FileExplorer(
                        file_count = 'single',
                        glob="**/*.json",
                        root=None,
                    )
                with gr.Column(scale=4,visible=False) as right_side:
                    json=gr.JSON()
        ############ DD PAGE
        Savefile_Des_btn.click( grfun.on_browse,inputs=Savefile_Des,outputs=Savefile_Des,   show_progress="hidden")
        Game_Des_btn.click(     grfun.on_browse,inputs=Game_Des,    outputs=Game_Des,       show_progress="hidden")
        Check_btn.click(        grfun.check_folders,inputs=[Savefile_Des,Game_Des],
                                outputs=[Savefile_Des,Game_Des,profile_page,profile_drop],  show_progress="hidden")
        profile_drop.change(grfun.select_profiles, inputs=[profile_drop],outputs=[data_page,mod_page])
        ############ MOD PAGE
        mod_page.select(grfun.mod_page,inputs=[profile_drop],outputs=[examples])
        examples.click( grfun.load_mod,
                        inputs=[examples], outputs=[Index,Image,Mod_Name,Source,Folder,Type,Enable])  
        Export.click(grfun.export_list, inputs=[], outputs=[])  
        Sort.click(grfun.sorted_by_type, inputs=[], outputs=[examples])
        Type.change(grfun.update_list, inputs=[Index,Type],outputs=[examples])
        Enable.change(grfun.mod_enabled, inputs=[Index,Enable],outputs=[examples])
        ############ DATA PAGE
        data_page.select(grfun.data_page,inputs=[profile_drop],outputs=[FileEpr])
        FileEpr.change(grfun.show_json,inputs=[FileEpr],outputs=[right_side,json])
    return demo
if __name__ == "__main__":
    #with open('mod.json', 'r',encoding="utf-8") as json_file:
    #    json_data = json.load(json_file)
    #mods = process_folders(Mods_Des)
    #json_data = process_json_data(json_data,mods)
    #list_data=Json2List(json_data)
    #sorted_by_type()
    demo=gradio_init()
    demo.launch()