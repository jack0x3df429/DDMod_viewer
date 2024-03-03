import json,Type,binp
def build_tree(folders, fields):
    def folder_find_leaves(folders,fields,index_lst,folder_dict):
        folder_index        =   index_lst["folder_index"]
        folder              =   folders[folder_index]
        parent              =   folder.parent
        folder_field        =   folder.field
        num_direct_childs   =   folder.num_direct_childs
        num_all_childs      =   folder.num_all_childs
        folder_dict.update({fields[folder_field].name:{}})
        if num_direct_childs <= 0:
                return
        while True:
            if index_lst["field_index"] == folder_field:
                index_lst["field_index"]+=1; continue
            '''print("#"*10)
            print("Folder_index",folder_index)
            print("Folder's field: %s"%folder_field)
            print("field_index",index_lst["field_index"])'''
            field = fields[index_lst["field_index"]]
            '''print("Field: %s"%field.name)
            print("Value: %s"%type(field.tipe.get_value()))'''
            num_direct_childs-=1
            #print("num_direct_childs:",num_direct_childs)
            ####################
            
            if isinstance(field.tipe,Type.Object):
                #print("#"*10)
                index_lst["folder_index"]+=1
                #print("Find Folder_index %s,\n have %s childs left, Entering..."%(index_lst["folder_index"],num_direct_childs))
                folder_find_leaves(folders,fields,index_lst,folder_dict[fields[folder_field].name])
                #print("#"*10)
                #print("Back to Folder_index %s,\nwho have %s childs left"%(folder_index,num_direct_childs))
            else:
                if not isinstance(field.tipe, binp.File):
                    folder_dict[fields[folder_field].name].update({field.name:field.tipe.get_value()})
                else:
                    folder_dict[fields[folder_field].name].update({field.name:field.tipe.write_to_json()})
            if num_direct_childs <= 0:
                return
            index_lst["field_index"]+=1
            

    folder_dict = {}
    # 建立 folder_dict，以 field_id 為 key
    index_lst={#做成Dict方便pass by reference
        "folder_index"  :0,
        "field_index"   :0
    }
    ##作一遞迴給obj找child用
    print("Build Tree With %s Folders, %s Field"%(len(folders),len(fields)))
    folder_find_leaves(folders,fields,index_lst,folder_dict)
    #print(folder_dict)
    return folder_dict

            

# 測試資料
if __name__ == '__main__':
    folders = [
        {"parent": None,"field": 0, "num_direct_childs": 4, "num_all_childs": 8},
        {"parent": 0,   "field": 2, "num_direct_childs": 2, "num_all_childs": 3},
        {"parent": 1,   "field": 4, "num_direct_childs": 1, "num_all_childs": 1},
        {"parent": 0,   "field": 7, "num_direct_childs": 1, "num_all_childs": 1}
    ]

    fields = [
        {"name": "0", "folder_id": None, "value": None},
        {"name": "a", "folder_id": 0, "value": "a"},
        {"name": "1", "folder_id": 0, "value": None},
        {"name": "b", "folder_id": 1, "value": "b"},
        {"name": "2", "folder_id": 1, "value": None},
        {"name": "c", "folder_id": 2, "value": "c"},
        {"name": "d", "folder_id": 0, "value": "d"},
        {"name": "3", "folder_id": 0, "value": None},
        {"name": "e", "folder_id": 3, "value": "e"}
    ]

    result = build_tree(folders, fields)
    print(json.dumps(result, indent = 4, ensure_ascii=False))
