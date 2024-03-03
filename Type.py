from typing import Optional
from collections import defaultdict
from struct import pack,unpack
from ddhash import ddhash,load_name_cache
hashmap=load_name_cache("names_cache.txt")

def btyeread( array : list[bytearray], l : int)-> bytearray:
    read  = array[0][:l]
    array[0] = array[0][l:]
    return read
class FieldType:
    def __init__(self, value):
        self._value = value
    def __eq__(self, other):
        return self._value == other._value
    def unwrap_object(self):
        if isinstance(self, Object):
            return self._value
        else:
            raise ValueError(f"attempted to unwrap non-object field type {self.field_type}")
    def unwrap_object_mut(self):
        return self.unwrap_object()  # 在Python中，返回的列表本來就是可變的
    def get_value(self):
        return self._value
# Enum variants
class Bool(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        return cls(unpack('<?',raw_data)[0])
    def to_buf(self):
        return pack('<?',self._value)
class TwoBool(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        return cls([unpack('<?',raw_data[0:1])[0], unpack('<?', raw_data[4:5])[0]])
    def to_buf(self):
        return pack('<ii',self._value[0],self._value[1])
class TwoInt(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        return cls([unpack('<i',raw_data[:4])[0], unpack('<i', raw_data[4:8])[0]])
    def to_buf(self):
        return pack('<ii',self._value[0],self._value[1]) 
class Int(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        value=unpack('<i', raw_data)[0]
        return cls(value)
    def to_buf(self):
        return pack('<i',self._value)
    def get_value(self):
        return hashmap[self._value] if self._value in hashmap else self._value
class Float(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        value=round(unpack('<f', raw_data)[0],5)
        return cls(value)
    def to_buf(self):
        return pack('<f',self._value)
class Char(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        char_value = unpack('<c', raw_data)[0]
        if char_value.isascii():
            char_value = char_value.decode('utf-8')
        else:
            raise ValueError("CharError")
        return cls(char_value)
    def to_buf(self):
        return pack('<c',self._value.encode('utf-8'))
class String(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        len_value = unpack('<i', raw_data[:4])[0]
        if len_value + 4 == len(raw_data):
            buf = raw_data[4:]
            string = buf.decode('utf-8', 'ignore')
        else:
            raise ValueError("UnknownField")
        return cls(string.rstrip("\x00"))
    def to_buf(self):
        buf = self._value.encode('utf-8', 'ignore')+b"\x00"
        return pack('<i',len(buf))+ buf
class IntVector(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        num = unpack('<I', raw_data[:4])[0]
        value=[unpack('<i', raw_data[4*_+4:4*_+8])[0] for _ in range(num)]
        return cls(value)
    def get_value(self):
        return [hashmap[v] if v in hashmap else v for v in self._value]
    def to_buf(self):
        buf = bytearray()
        for v in self._value:
            buf += pack('<i',v)
        return pack('<I',len(self._value))+ buf
class StringVector(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        raw_data=[raw_data]
        num = unpack('<I', btyeread(raw_data,4))[0]
        value=[]
        to_skip = 0
        for _ in range(num):
            btyeread(raw_data,to_skip)
            len_value = unpack('<I', btyeread(raw_data,4))[0]
            buf = btyeread(raw_data,len_value)
            string = buf.decode('utf-8', 'ignore').rstrip("\x00")
            value.append(string)
            to_skip = ( 0, 4-(len_value % 4 ))[ len_value%4>0 ]
        return cls(value)
    def to_buf(self):
        buf = bytearray()
        to_skip = 0
        for v in self._value:
            len_value = len(v)+1
            buf += b'\x00'*(to_skip) + pack('<I',len_value) + v.encode('utf-8', 'ignore') + b'\x00'
            to_skip = ( 0, 4-(len_value % 4 ))[ len_value%4>0 ]
        return pack('<I',len(self._value))+ buf
class FloatArray(FieldType):
    def __init__(self, value):
        super().__init__(value)
    @classmethod
    def from_buf(cls,raw_data):
        num=len(raw_data)//4
        return cls([unpack('<f', raw_data[4*_:4*_+4])[0] for _ in range(num)])
    def to_buf(self):
        buf = bytearray()
        for v in self._value:
            buf += pack('<f',v)
        return buf
class File(FieldType):
    def __init__(self, value):
        super().__init__(value)
class Object(FieldType):
    def __init__(self, value=None):
        super().__init__(value)
    def to_buf(self):
        buf = bytearray()
        for v in self._value:
            buf += pack('<f',v)
        return buf
formatted_dict = {
    "requirement_code": Char,
    "current_hp": Float,
    "m_Stress": Float,
    "actor": {
        "current_hp":Float,
        "buff_group": {
            "*": {
                "amount": Float
            }
        }
    },
    "chapters": {
        "*": {
            "*": {
                "percent": Float
            }
        }
    },
    "non_rolled_additional_chances": {
        "*": {
            "chance": Float
        }
    },
    "rarity_table": {
        "*": {
            "chance": Float
        }
    },
    "chance_of_loot": Float,
    "shard_consume_percent": Float,
    "chances": {
        "*": Float
    },
    "chance_sum": Float,
    "read_page_indexes": IntVector,
    "raid_read_page_indexes": IntVector,
    "raid_unread_page_indexes": IntVector,
    "dungeons_unlocked": IntVector,
    "played_video_list": IntVector,
    "trinket_retention_ids": IntVector,
    "last_party" : {
            "last_party_guids" : IntVector
    },#    "last_party_guids": IntVector,
    "dungeon_history": IntVector,
    "buff_group_guids": IntVector,
    "result_event_history": IntVector,
    "dead_hero_entries": IntVector,
    "additional_mash_disabled_infestation_monster_class_ids": IntVector,
    "mash": {
        "valid_additional_mash_entry_indexes": IntVector
    },
    "party": {
        "heroes": IntVector
    },
    "skill_cooldown_keys": IntVector,
    "skill_cooldown_values": IntVector,
    "bufferedSpawningSlotsAvailable": IntVector,
    "curioGroups": {
        "*": {
            "curios": IntVector,
            "curio_table_entries": IntVector
        }
    },
    "raid_finish_quirk_monster_class_ids": IntVector,
    "narration_audio_event_queue_tags": IntVector,
    "dispatched_events": IntVector,
    "backer_heroes": {
        "*": {
            "combat_skills": IntVector,
            "camping_skills": IntVector,
            "quirks": IntVector
        }
    },
    "goal_ids": StringVector,
    "roaming_dungeon_2_ids": {
        "*": {
            "s": StringVector
        }
    },
    "quirk_group": StringVector,
    "backgroundNames": StringVector,
    "backgroundGroups": {
        "*": {
            "backgrounds": StringVector,
            "background_table_entries": StringVector
        }
    },
    "map": {
        "bounds": FloatArray
    },
    "areas": {
        "*": {
            "bounds": FloatArray,
            "tiles": {
                "*": {
                    "mappos": FloatArray,
                    "sidepos": FloatArray
                }
            }
        }
    },
    "killRange": TwoInt,
    "profile_options": {
        "values": {
            "quest_select_warnings": TwoBool,
            "provision_warnings": TwoBool,
            "deck_based_stage_coach": TwoBool,
            "curio_tracker": TwoBool,
            "dd_mode": TwoBool,
            "corpses": TwoBool,
            "stall_penalty": TwoBool,
            "deaths_door_recovery_debuffs": TwoBool,
            "retreats_can_fail": TwoBool,
            "multiplied_enemy_crits": TwoBool
        }
    },#####
    "item_tracking" : {
        "supply" : {
            "*" : {
                "buff_group_guids":IntVector
            }
        }
    }
}
def hardcoded_type(parents: list[str], name: str):
    d=formatted_dict.copy()
    path=parents.copy()
    if path[0] == "base_root":
        path.pop(0)
    path.append(name)
    if len(path)<=0: return False
    for idx,p in enumerate(path):
        if p in d:
            d = d.get(p,False)
        elif '*' in d and idx+1 < len(path):
            d = d.get('*',False)
        else:
            d=False
            break
    if d == False:
        return formatted_dict.get(path[-1],False) # last try
    else:
        return d
def dict_type(data):
    if isinstance(data,dict):
        return Object()
    elif isinstance(data,list):
        type_set = set([type(d) for d in data])
        if len(type_set)==1:
            if bool in type_set:
                return TwoBool(data)
            elif float in type_set:
                return FloatArray(data)
            elif int in type_set:
                return TwoInt(data)
            elif str in type_set:
                return StringVector(data)
        else:
            return IntVector(data)
    else:
        if isinstance(data,bool):
            return Bool(data)
        elif isinstance(data,int):
            return Int(data)
        elif isinstance(data,float):
            return Float(data)
        elif isinstance(data,str):
            return String(data)
        