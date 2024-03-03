import functools
class ddhash:
    def __init__(self):
        return
    def s_hash(s):
        acc = 0
        for c in s:
            acc = (acc * 53 + ord(c)) & 0xFFFFFFFF
            acc = (acc & 0x7FFFFFFF) - (acc >> 31) * 2**31
        return acc
def load_name_cache(file):
    name_dict={}
    with open(file,'r') as read:
        for line in read:
            name_dict.setdefault(ddhash.s_hash(line.strip()),"###%s"%line.strip())
    return name_dict