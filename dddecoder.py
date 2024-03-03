from typing import List, Any, IO, Optional, Union
from io import BufferedReader, BufferedWriter, BytesIO, IOBase, TextIOBase
import json, binp
from ddhash import ddhash

class dddecoder:
    def __init__(self,buffer=None):
        self.buffer = buffer
        self.json = None
        self.file_data=dict()
    @classmethod
    def decode_file(cls,file):
        f=open(file, 'rb')
        buffer = bytearray(f.read())
        f.close()
        return cls(buffer)
    def decode(self):
        print("######################################")
        self.file_data = binp.File.try_from_bin(self.buffer)
    def data2json(self,ret=False,file="out.json"):
        if isinstance(self.file_data, binp.File):
            out=dict()
            out = self.file_data.write_to_json()
            print("######################################")
            if ret:
                return out
            else:
                out=json.dumps(out, indent = 4, ensure_ascii=False)
                with open(file, "w",  encoding='utf-8') as outfile: 
                    outfile.write(out)
        else:
            return "Error: File does not appear to be a save file"
    def encode(self,file):
        f=open(file, 'wb')
        f.write(self.file_data.write_to_bin())
        f.close()
    def load_from_json(self,file):
        with open(file, 'r',  encoding='utf-8') as f:
            data = json.load(f)
            self.load_from_dict(data)
    def load_from_dict(self, dict_data):
        self.file_data=binp.File.load_from_dict(dict_data)