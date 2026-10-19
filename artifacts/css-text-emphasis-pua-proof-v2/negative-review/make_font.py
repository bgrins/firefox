import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'testing/web-platform/tests/fonts/Ahem.ttf'

def u16(data, offset):
    return struct.unpack_from('>H', data, offset)[0]

def checksum(data):
    data += bytes(-len(data) % 4)
    return sum(struct.unpack('>' + 'I' * (len(data) // 4), data)) & 0xffffffff

def layout(feature, lookup_type, subtable):
    language = struct.pack('>HHHH', 0, 0xffff, 1, 0)
    script = struct.pack('>HH', 4, 0) + language
    scripts = struct.pack('>H4sH', 1, b'DFLT', 8) + script
    features = struct.pack('>H4sHHHH', 1, feature, 8, 0, 1, 0)
    lookup = struct.pack('>HHHH', lookup_type, 0, 1, 8) + subtable
    lookups = struct.pack('>HH', 1, 4) + lookup
    return struct.pack('>IHHH', 0x10000, 10, 10+len(scripts), 10+len(scripts)+len(features)) + scripts + features + lookups

def main():
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == 'b719ecb31c5b21fc573c03f6421c74ac63c271a5a3ff841e34f9705fb94b8448'
    tables = {}
    for i in range(u16(source,4)):
        tag, _, offset, size = struct.unpack_from('>4sIII',source,12+16*i)
        tables[tag]=source[offset:offset+size]
    cmap=tables[b'cmap']
    mapping={}
    for cp in [65,66,67]:
        values=set()
        for i in range(u16(cmap,2)):
            offset=struct.unpack_from('>I',cmap,8+8*i)[0]
            if u16(cmap,offset)!=4:continue
            count=u16(cmap,offset+6)//2
            for j in range(count):
                end=u16(cmap,offset+14+2*j)
                start=u16(cmap,offset+16+2*count+2*j)
                if start<=cp<=end:
                    delta=u16(cmap,offset+16+4*count+2*j)
                    pointer=offset+16+6*count+2*j
                    distance=u16(cmap,pointer)
                    glyph=u16(cmap,pointer+distance+2*(cp-start)) if distance else cp
                    values.add((glyph+delta)&0xffff if glyph or not distance else 0)
                    break
        assert len(values)==1 and 0 not in values
        mapping[cp]=values.pop()
    a,b,c=(mapping[cp] for cp in [65,66,67])
    ligature=struct.pack('>HHH',c,2,b)
    ligset=struct.pack('>HH',1,4)+ligature
    substitution=struct.pack('>HHHH',1,8+len(ligset),1,8)+ligset+struct.pack('>HHH',1,1,a)
    tables[b'GSUB']=layout(b'liga',4,substitution)
    positioning=struct.pack('>HHHhHHH',1,8,4,-2500,1,1,c)
    tables[b'GPOS']=layout(b'kern',1,positioning)
    tables[b'head']=tables[b'head'][:8]+bytes(4)+tables[b'head'][12:]
    count=len(tables);selector=count.bit_length()-1;search=16*(1<<selector)
    header=struct.pack('>IHHHH',0x10000,count,search,selector,16*count-search)
    directory=bytearray();payload=bytearray();head=None
    for tag,data in sorted(tables.items()):
        offset=12+16*count+len(payload)
        directory+=struct.pack('>4sIII',tag,checksum(data),offset,len(data))
        payload+=data+bytes(-len(data)%4)
        if tag==b'head':head=offset
    font=bytearray(header+directory+payload)
    struct.pack_into('>I',font,head+8,(0xb1b0afba-checksum(font))&0xffffffff)
    assert checksum(font)==0xb1b0afba
    (OUT/'negative-ligature.ttf').write_bytes(font)
    record={'source':str(SOURCE),'source_sha256':hashlib.sha256(source).hexdigest(),'output_sha256':hashlib.sha256(font).hexdigest(),'mapping':mapping,'units_per_em':u16(tables[b'head'],18),'GSUB':'liga AB -> C','GPOS':'kern C xAdvance -2500','table_sizes':{tag.decode():len(data) for tag,data in tables.items()}}
    (OUT/'FONT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
