from ddhash import ddhash,load_name_cache
from struct import pack, unpack
from typing import Optional
from empty_class import Header,Objects,FieldInfo,Fields,Data,File,BinObjectFrame,FieldType
import mod
from mod import ObjIdx,ObjectInfo,FieldIdx,Field
dbg=[]
import Type,build_tree
'''
OBJ↓
    ObjectInfo↓
        parent: Optional[int]
        field: int (Object的Field位置)
        num_direct_childs:int
        num_all_childs: int
'''
'''
Data↓
    Field↓
        name:   str
        parent: int (Object的Id)
        tipe:   FieldType↓
                    value
BinObjectFrame↓
        obj_idx:    ObjIdx
        field_idx:  FieldIdx
        num_childs: int
        name:   str    
'''
def btyeread( array : list[bytearray], l : int)-> bytearray:
    read  = array[0][:l]
    array[0] = array[0][l:]
    return read
def btyewrite( array : list[bytearray], l : int, bytearray)-> bytearray:
    read  = array[0][:l]
    array[0] = array[0][l:]
    return read
class Header:
    BIN_SIZE = 64
    MAGIC_NUMBER = b'\x01\xB1\x00\x00'
    def __init__(self, full_len, magic, version, header_len, objects_size, objects_num,
                 objects_offset, fields_num, fields_offset, data_size, data_offset):
        self.full_len = full_len
        self.magic = magic
        self.version = version
        self.header_len = header_len
        self.objects_size = objects_size
        self.objects_num = objects_num
        self.objects_offset = objects_offset
        self.fields_num = fields_num
        self.fields_offset = fields_offset
        self.data_size = data_size
        self.data_offset = data_offset
    @classmethod
    def try_from_bin(cls, reader: bytearray):
        buf = reader[:64]
        #print(buf)
        #buf = reader.read(cls.BIN_SIZE)
        #print(len(buf),reader)
        if len(buf) != cls.BIN_SIZE:
            raise "Not enough data for header"

        magic = buf[:4]
        if magic != cls.MAGIC_NUMBER:
            raise "Not a valid binary file"

        version, header_len, _, objects_size, objects_num, objects_offset, _, _, fields_num, fields_offset, _, data_size, data_offset = unpack('<IIIIIIQQIIIII', buf[4:])

        calc_offset_objects = objects_offset + objects_num * 16
        calc_offset_fields = fields_offset + fields_num * 12
        full_len =len(reader)
        print("full_len:\t\t%d Bytes"%full_len)
        print("magic:\t\t\t%s"%magic)
        print("version:\t\t%d"%version)
        print("header_len:\t\t%d Bytes"%header_len)
        print("objects_size:\t\t%d Bytes"%objects_size)
        print("objects_num:\t\t%d 節點"%objects_num)
        print("objects_offset:\t\t%d"%objects_offset)
        print("fields_size:\t\t%d Bytes"%(fields_num *12))
        print("fields_num:\t\t%d 資料行"%fields_num)
        print("fields_offset:\t\t%d"%fields_offset)
        print("data_size:\t\t%d Bytes"%data_size)
        print("data_offset:\t\t%d"%data_offset)
        print("######################################")
        return cls(
            full_len,
            magic,
            version,
            header_len,
            objects_size,
            objects_num,
            objects_offset,
            fields_num,
            fields_offset,
            data_size,
            data_offset), reader[64:]
    def write_to_bin(self, writer: bytearray):
        header=self.magic+pack('<IIIIIIQQIIIII',
            self.version, 
            self.header_len, 
            0, 
            self.objects_size, 
            self.objects_num, 
            self.objects_offset,
            0, 
            0, 
            self.fields_num, 
            self.fields_offset, 
            0, 
            self.data_size, 
            self.data_offset)
        #print(header)
        #calc_offset_objects = objects_offset + objects_num * 16
        #calc_offset_fields = fields_offset + fields_num * 12
        writer+=header
        return writer
    def calc_bin_size(self) -> int:
        return self.BIN_SIZE
    @classmethod
    def from_dict(cls,f:Fields,o: Objects, d: Data):
        #print(d.get_type_count())
        magic   =  cls.MAGIC_NUMBER
        version =  1685651456
        header_len = cls.BIN_SIZE
        objects_size = len(o.objs)*16
        objects_num = len(o.objs)
        objects_offset = 64
        fields_size = len(f.fields)*12
        fields_num = len(f.fields)
        fields_offset = objects_size + objects_offset
        data_size = d.datsize
        data_offset = fields_offset + fields_size
        full_len = data_size + data_offset
        print("full_len:\t\t%d Bytes"%full_len)
        print("magic:\t\t\t%s"%magic)
        print("version:\t\t%d"%version)
        print("header_len:\t\t%d Bytes"%header_len)
        print("objects_size:\t\t%d Bytes"%objects_size)
        print("objects_num:\t\t%d 節點"%objects_num)
        print("objects_offset:\t\t%d"%objects_offset)
        print("fields_size:\t\t%d Bytes"%(fields_num *12))
        print("fields_num:\t\t%d 資料行"%fields_num)
        print("fields_offset:\t\t%d"%fields_offset)
        print("data_size:\t\t%d Bytes"%data_size)
        print("data_offset:\t\t%d"%data_offset)
        print("######################################")
        return cls(
            full_len,
            magic,
            version,
            header_len,
            objects_size,
            objects_num,
            objects_offset,
            fields_num,
            fields_offset,
            data_size,
            data_offset)
class Objects:  #每個分支物件
    def __init__(self, objs):
        self.objs = objs      
    @classmethod
    def try_from_bin(cls, reader: bytearray, header) -> 'Objects':
        objs = []
        buf_size = 16
        buf = bytearray(buf_size)
        reader=[reader]
        for _ in range(header.objects_num):
            buf = btyeread(reader,buf_size)
            parent = unpack("<i", buf[:4])[0]
            field = unpack("<I", buf[4:8])[0]
            num_direct_childs = unpack("<I", buf[8:12])[0]
            num_all_childs = unpack("<I", buf[12:])[0]

            objs.append(ObjectInfo(
                parent if parent >= 0 else None,
                field,
                num_direct_childs,
                num_all_childs
            ))
            #print(parent,field,num_direct_childs,num_all_childs)
        return cls(objs),reader[0]
    def write_to_bin(self, writer: bytearray) -> None:
        buf_size = 4 * 4
        buf = bytearray(buf_size)
        for o in self.objs:
            buf[:4] = pack("<i", o.parent if o.parent is not None else -1)
            buf[4:8] = pack("<I", o.field)
            buf[8:12] = pack("<I", o.num_direct_childs)
            buf[12:] = pack("<I", o.num_all_childs)
            writer+=buf
        return writer
    def calc_bin_size(self) -> int:
        return 4 * 4 * len(self.objs)
class FieldInfo:
    #0111 1111 1111 1111 1111 1111 1111 1111
    #object_index(20bits) name_length(9bits) _(1bit) is_object(1bits)
    NAME_LEN_BITS = 0b1_1111_1111
    OBJ_IDX_BITS = 0b1111_1111_1111_1111_1111
    def __init__(self, name_hash, offset, field_info: int,ori=None):
        self.name_hash  = name_hash
        self.offset     = offset
        self.field_info = field_info
        self.ori        = ori
        #self.objidx = None
    def is_object(self):
        return (self.field_info & 0b1) == 1

    def name_length(self):
        return (self.field_info >> 2) & self.NAME_LEN_BITS

    def object_index(self):
        if self.is_object():
            return (self.field_info >> 11) & self.OBJ_IDX_BITS
        else:
            return None
class Fields:   #每一橫行 ※不包刮符號
    def __init__(self, fields,rdr=None):
        self.fields = fields
        self.rdr=rdr
    @classmethod
    def try_from_bin(cls, reader: bytearray, header) -> 'Fields':
        fields = []
        buf_size = 12
        rdr=reader
        for _ in range(header.fields_num):
            name_hash = unpack("<i", reader[:4])[0]
            offset = unpack("<I", reader[4:8])[0]
            field_info = unpack("<I", reader[8:12])[0] & ~0x8000_0000
            fields.append(FieldInfo(
                name_hash,
                offset,
                field_info
            ))
            #print(name_hash,offset,field_info)
            reader=reader[buf_size:]
        return cls(fields,rdr),reader
    def write_to_bin(self, writer: bytearray,d):
        buf_size = 12
        for o in self.fields:
            buf = bytearray(buf_size)
            buf[:4] = pack("<i", o.name_hash)
            buf[4:8]= pack("<I", o.offset)
            buf[8:] = pack("<I", o.field_info)
            writer+=buf
        return writer
    @classmethod
    def from_dict(cls,o: Objects, d: Data):
        fields = []
        offset=0
        obj_idx = 0
        #object_index(20bits) name_length(9bits) _(1bit) is_object(1bits)
        for data in d.dat:
            if int(isinstance(data.tipe,Type.Object)):
                field_info = obj_idx
                obj_idx += 1
            else:
                field_info = 0
            field_info <<= 9
            field_info += len(data.name)+1
            field_info <<= 2
            field_info +=int(isinstance(data.tipe,Type.Object))
            fields.append(FieldInfo(
                ddhash.s_hash(data.name),
                offset,
                field_info
            ))
            #print(d.name,offset,field_info)
            offset1=offset
            offset,a = data.add_bin_size(offset)
            '''if offset1 ==7686:
                print(data.name,data.tipe.get_value())
                print(offset-offset1)'''
            #print(offset)
        d.datsize = offset
        return cls(fields),d
class Data:
    def __init__(self, dat=None):#使用[]會導致所有dat共通
        if dat is None:
            self.dat = []
        else:
            self.dat = dat
        self.datsize=None
        self.type_c={   Type.Bool:0,
                        Type.TwoBool:0,
                        Type.Int:0,
                        Type.Float:0,
                        Type.Char:0,
                        Type.String:0,
                        Type.IntVector:0,
                        Type.StringVector:0,
                        Type.FloatArray:0,
                        Type.Object:0,
                        File:0}
    def get_type_count(self):
        for d in self.dat:
            self.type_c[type(d.tipe)]+=1
        return self.type_c
class File:
    BUILTIN_VERSION_FIELD = "__revision_dont_touch"
    def __init__(self, h: Header, o: Objects, f: Fields, d: list,rdr=None):
        self.h = h
        self.o = o
        self.f = f
        self.d = d
        self.wtr=None
        self.rdr=rdr
    @classmethod
    def try_from_bin(cls, reader: bytearray) -> 'File':
        rdr=reader
        h, reader = Header.try_from_bin(reader)
        o, reader = Objects.try_from_bin(reader, h)
        f, reader = Fields.try_from_bin(reader, h)
        d = cls.decode_fields_bin(reader, f, o, h)
        #print(d.get_type_count())
        return cls(h, o, f, d, rdr)
    def calc_bin_size(self) -> int:
        meta_size = self.h.calc_bin_size() + self.o.calc_bin_size() + self.f.calc_bin_size()
        existing_size = sum(f.add_bin_size(0) for f in self.dat)
        return meta_size + existing_size
    def write_to_bin(self):
        writer=bytearray()
        writer=self.h.write_to_bin(writer)
        writer=self.o.write_to_bin(writer)
        writer=self.f.write_to_bin(writer,self.d)
        writer=self.encode_fields_bin(writer,self.f,self.d)
        return writer
    def write_to_json(self) -> None:
        d_={
            self.BUILTIN_VERSION_FIELD  : self.h.version
            }
        d_.update(build_tree.build_tree(self.o.objs,self.d.dat))
        return d_
    @classmethod
    def load_from_dict(cls, dict_data)-> 'File':
        d,o=cls.data_from_dict(dict_data)
        f,d     =Fields.from_dict(o,d)
        h       =Header.from_dict(f,o,d)
        return cls(h, o, f, d)
    def to_buf(self):
        buf=self.write_to_bin()
        return pack('<i',len(buf))+buf
    def get_value(self):
        return "This is File"
    @classmethod
    def decode_fields_bin(cls,reader: bytearray, f: Fields, o: Objects, header: Header):
        global dbg
        max_size = header.data_size
        buf = reader[:max_size]
        offset_sizes = {}
        offsets = sorted([f.offset for f in f.fields])
        for offs in zip(offsets, offsets[1:]):
            offset_sizes[offs[0]] = offs[1] - offs[0]
        if offsets:
            offset_sizes[offsets[-1]] = max_size - offsets[-1]
        data = Data()
        obj_stack = []
        
        for idx, field in enumerate(f.fields):
            off = field.offset
            len_name = field.name_length()
            field_name = buf[off:off + len_name]
            name = field_name.decode('utf-8', 'ignore').rstrip('\x00')
            #######################Field##########################
            #print(name,':')
            #print("\t\t",off,"\t",len_name,end='\t')

            #print(field_name,name,ddhash.s_hash(name),field.name_hash)
            if ddhash.s_hash(name) != field.name_hash:
                raise ValueError("Hash mismatch")
            data_begin = off + len_name
            data_end = off + offset_sizes[field.offset]
            
            field.ori=buf[off : data_end]
            #field.ori=field_name
            if field.is_object():
                obj_idx = field.object_index()
                num_childs = o.objs[obj_idx].num_direct_childs
                field_type = Type.Object([FieldIdx.dangling() for _ in range(num_childs)])
                #print(name,num_childs,len(field_type.get_value()))
            else:
                if data_end <= data_begin:
                    return ValueError("FormatErr")
                to_skip_if_aligned = ( 0, 4-(data_begin % 4 ))[ data_begin%4>0 ]
                field_data = buf[data_begin:data_end]
                #field.ori=buf[data_begin:data_end]
                field_type = FieldType.try_from_bin(
                    field_data,
                    to_skip_if_aligned,
                    data_end - data_begin,
                    [p.name for p in obj_stack],
                    name)
            #print(len(field_type.get_value()))
            #print(len(data.dat))
            data.dat.append(#obj_stack[-1].obj_idx: Parent的obj id
                Field(name, obj_stack[-1].obj_idx if obj_stack else None, field_type)
            )
            #print(len(data.dat[0].tipe.get_value()))
            if obj_stack:
                #print(len(data.dat))
                #print(name,obj_stack[0].name,field,obj_stack[0].num_childs,len(data.dat[obj_stack[-1].field_idx].tipe.get_value()))
                frame = obj_stack[-1]
                childs = data.dat[frame.field_idx].tipe.unwrap_object_mut()
                #print(len(childs),frame.name,frame.num_childs,frame.field_idx)
                childs[frame.num_childs] = FieldIdx(idx)
                frame.num_childs += 1
            elif not field.is_object():
                return ValueError("FormatErr")
            
            if field.is_object():
                obj_idx = field.object_index()
                field_idx = o.objs[obj_idx].field
                if not isinstance(data.dat[field_idx].tipe, Type.Object):
                    return ValueError("FormatErr")
                obj_stack.append(BinObjectFrame(obj_idx, field_idx, 0, name))

            #num_direct_childs: 直系子物件數量，非隔代
            #print(obj_stack[-1].name,o.objs[obj_stack[-1].obj_idx].num_direct_childs)
            #print(obj_stack[-1].num_childs,o.objs[obj_stack[-1].obj_idx].num_direct_childs)
            while obj_stack and obj_stack[-1].num_childs == o.objs[obj_stack[-1].obj_idx].num_direct_childs:
                obj_stack.pop()
        return data
    @classmethod
    def encode_fields_bin(cls,writer: bytearray, f: Fields, d: Data):
        offset=0
        for field_idx in range(len(d.dat)):
            field = f.fields[field_idx]
            data = d.dat[field_idx]
            field.offset=offset
            name=data.name
            len_name = field.name_length()
            tipe=data.tipe
            size=offset
            ty=type(tipe)
            if offset != offset:
                print("!offset Error",field_idx)
            offset,a=data.add_bin_size(offset)
            '''if size ==7686:
                print(data.name,data.tipe.get_value())
                print(offset-size)'''
            size=offset-size
            if not ty==Type.Object:
                buf = name.encode('utf-8')+b"\x00"*(size-len_name-len(tipe.to_buf())+1)+tipe.to_buf()
                #if  buf != field.ori:
                '''if  tipe.to_buf() != field.ori[-len(tipe.to_buf()):]:
                    if ty not in (File,Type.Float):
                        print(ty)
                        print(tipe.to_buf())
                        print(bytes(field.ori[-len(tipe.to_buf()):]))
                        print(bytes(field.ori[:len_name]))
                        print(tipe.get_value())
                        print(bytes(field.ori[len_name:len_name+a]))
                        print(buf,len(buf))
                        print(bytes(field.ori),len(field.ori))
                        for i in range(max(len(buf),len(field.ori))):
                            if buf[i] != field.ori[i]:
                                print(i,buf[i:i+1],field.ori[i:i+1])'''
                writer+=buf
            else:
                writer+=name.encode('utf-8')+b"\x00"
        return writer
    @classmethod
    def data_from_dict(cls,dict_data):
        def nest_data(items,parent=None):
            num_childs = len(items)
            for key,value in items:
                field_type=Type.dict_type(value)
                if isinstance(field_type,Type.Object):
                    obj.append(ObjectInfo(
                            parent=parent,
                            field=len(dat),
                            num_direct_childs=len(value),
                            num_all_childs=0
                    ))
                    i=len(obj)-1
                    dat.append(Field(key, len(obj), field_type))
                    sub_childs = nest_data(value.items(),parent=len(obj)-1)
                    obj[i].num_all_childs=sub_childs
                    num_childs += sub_childs
                else:
                    dat.append(Field(key, len(obj), field_type))
            return num_childs
        ##########################################################
        dat=[]
        obj=[]
        dat.append(Field("base_root", None, Type.Object([FieldIdx.dangling() for _ in range(len(dict_data["base_root"]))])))
        obj.append(ObjectInfo(
                            parent=-1,
                            field=0,
                            num_direct_childs=len(dict_data["base_root"]),
                            num_all_childs=0,
        ))

        all_fields = nest_data(dict_data["base_root"].items(),0)
        obj[0].num_all_childs=all_fields
        #for v in obj:
        #    print(v.parent,v.field,v.num_direct_childs,v.num_all_childs)
        return Data(dat),Objects(obj)
class BinObjectFrame:
    def __init__(self, obj_idx: ObjIdx, field_idx: FieldIdx, num_childs: int, name: str):
        self.obj_idx = obj_idx
        self.field_idx = field_idx
        self.num_childs = num_childs
        self.name = name
class FieldType:
    @classmethod
    def try_from_bin(
        cls,
        reader,
        to_skip_if_aligned: int,
        max_len: int,          #存放Json物件位元數
        paths: list[str], #存放Json上級物件路徑
        name: str
    )-> Type.FieldType: 
        ret_val=None
        reader=[reader] #prepare for passby reference
        #print(name)
        if name == "raw_data" or name == "static_save":
            cls._skip(reader, to_skip_if_aligned)
            len_value = unpack('<i', btyeread(reader,4))[0]
            #print(name,len_value,max_len,to_skip_if_aligned)
            if len_value + 4 == max_len - to_skip_if_aligned:
                return File.try_from_bin(btyeread(reader,len_value))
            else:
                raise ValueError("UnknownField")
        elif val := Type.hardcoded_type(paths, name):
            if val==Type.Float:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,4))
            elif val ==Type.IntVector:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,max_len))
            elif val == Type.StringVector:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,max_len))
            elif val == Type.FloatArray:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,max_len - to_skip_if_aligned))
            elif val == Type.TwoInt:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,8))
            elif val == Type.TwoBool:
                cls._skip(reader, to_skip_if_aligned)
                ret_val=val.from_buf(btyeread(reader,8))
            elif val == Type.Char:
                ret_val=val.from_buf(btyeread(reader,4))
            else:
                raise ValueError("Unhandled hardcoded type when reading")
            return ret_val
        else:
            if max_len == 1:
                return Type.Bool.from_buf(btyeread(reader,1))
            else:
                aligned_max_len = max_len - to_skip_if_aligned
                cls._skip(reader, to_skip_if_aligned)
                if aligned_max_len == 4:
                    return Type.Int.from_buf(btyeread(reader,4))
                elif 5 <= aligned_max_len <= float('inf'):
                    #print(name)
                    return Type.String.from_buf(btyeread(reader,aligned_max_len))
                else:
                    raise ValueError("UnknownField")
        
    @staticmethod
    def _skip(reader, to_skip: int):
        btyeread(reader,to_skip)

