from ddhash import ddhash
from struct import pack, unpack
from typing import Optional
import Type,binp
class ObjectInfo:
    def __init__(self, parent: Optional[int], field: int, num_direct_childs: int, num_all_childs: int = 0):
        self.parent = parent
        self.field = field
        self.num_direct_childs = num_direct_childs
        self.num_all_childs = num_all_childs
class ObjIdx:
    def __init__(self, value):
        self.value = value

    def numeric(self) -> int:
        return int(self.value)
class FieldIdx:
    def __init__(self, value):
        self.value = value
    def numeric(self) -> int:
        return int(self.value)
    @classmethod
    def dangling(self):
        return self(0xFFFFFFFF)
class Field:
    def __init__(self, name, parent, tipe):
        self.name = name
        self.parent = parent
        self.tipe = tipe
    def __eq__(self, other):
        return (
            isinstance(other, Field) and
            self.name == other.name and
            self.parent == other.parent and
            self.tipe == other.tipe
        )
    def to_name_list(self):
        return [ p.name for p in self.parent]
    def add_bin_size(self, existing_size=0):
        existing_size += len(self.name) + 1
        align = ((existing_size + 3) & ~0b11) - existing_size
        if isinstance(self.tipe, Type.Bool):
            existing_size += 1
        elif isinstance(self.tipe, Type.TwoBool):
            existing_size += align + 8
        elif isinstance(self.tipe, Type.Int):
            existing_size += align + 4
        elif isinstance(self.tipe, Type.Float):
            existing_size += align + 4
        elif isinstance(self.tipe, Type.Char):
            existing_size += 1
        elif isinstance(self.tipe, Type.String):
            #print(align,len(self.tipe.get_value()),self.tipe.get_value().encode('utf-8'))
            existing_size += align + 4 + len(self.tipe.get_value().encode('utf-8')) + 1
        elif isinstance(self.tipe, Type.IntVector):
            existing_size += align + 4 + len(self.tipe.get_value()) * 4
        elif isinstance(self.tipe, Type.StringVector):
            tmp_size = 4
            for s in self.tipe.get_value():
                tmp_size = (tmp_size + 3) & ~0b11
                tmp_size += 4
                tmp_size += len(s) + 1
            existing_size += tmp_size + align
        elif isinstance(self.tipe, Type.FloatArray):
            existing_size += align + 4 * len(self.tipe.get_value())
        elif isinstance(self.tipe, Type.TwoInt):
            existing_size += align + 8
        elif isinstance(self.tipe, binp.File):
            if self.tipe is not None:
                existing_size += align + 4 + self.tipe.h.full_len
            else:
                raise ValueError("file already en-/decoded")
        elif isinstance(self.tipe, Type.Object):
            pass
        else:
            raise ValueError(f"Unknown FieldType: {self.tipe}")

        return existing_size,align
class NameType:
    def __init__(self, name):
        self.name = name.rstrip("\x00")
class FromBinError:
    pass