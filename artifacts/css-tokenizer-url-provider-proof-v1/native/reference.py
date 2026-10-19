"""Independent CSS Syntax scalar algorithms, retaining raw-source endpoints."""
WS=' \t\n'
HEX='0123456789abcdefABCDEF'

def preprocess(source):
    units=[];i=0;offset=0
    while i<len(source):
        c=source[i];width=len(c.encode());i+=1
        if c=='\r':
            if i<len(source) and source[i]=='\n':width+=1;i+=1
            c='\n'
        elif c=='\f':c='\n'
        elif c=='\0':c='\ufffd'
        offset+=width;units.append((c,offset))
    return units

def metadata(source,offset):
    prefix=source.encode()[:offset].decode();line=0;column=1;i=0
    while i<len(prefix):
        c=prefix[i];i+=1
        if c=='\r':
            if i<len(prefix) and prefix[i]=='\n':i+=1
            line+=1;column=1
        elif c in '\n\f':line+=1;column=1
        else:column+=2 if ord(c)>0xffff else 1
    return line,column

class Reference:
    def __init__(self,source):
        self.source=source;self.units=preprocess(source);self.text=''.join(c for c,_ in self.units);self.i=0;self.seen=False
    def peek(self,n=0):
        return self.text[self.i+n] if self.i+n<len(self.text) else None
    def valid_escape(self):
        return self.peek()=='\\' and self.peek(1)!='\n'
    def escape(self):
        assert self.peek()=='\\';self.i+=1;c=self.peek()
        if c is None:return '\ufffd'
        if c in HEX:
            digits=''
            while self.peek() is not None and self.peek() in HEX and len(digits)<6:
                digits+=self.peek();self.i+=1
            if self.peek() is not None and self.peek() in WS:self.i+=1
            value=int(digits,16)
            return '\ufffd' if value==0 or 0xd800<=value<=0xdfff or value>0x10ffff else chr(value)
        self.i+=1;return c
    def name(self):
        out=''
        while self.peek() is not None:
            c=self.peek()
            if c.isascii() and (c.isalnum() or c in '_-') or ord(c)>=128:
                out+=c;self.i+=1
            elif self.valid_escape():out+=self.escape()
            else:break
        return out
    def bad(self):
        while self.peek() is not None:
            if self.peek()==')':self.i+=1;return
            if self.valid_escape():self.escape()
            else:self.i+=1
    def url(self):
        out=''
        while self.peek() is not None and self.peek() in WS:self.i+=1
        while self.peek() is not None:
            c=self.peek()
            if c==')':self.i+=1;return 'url',out
            if c in WS:
                while self.peek() is not None and self.peek() in WS:self.i+=1
                if self.peek()==')':self.i+=1;return 'url',out
                if self.peek() is None:return 'url',out
                self.bad();return 'bad-url',None
            if c in '\"\'(' or ord(c) in [*range(1,9),11,*range(14,32),127]:
                self.i+=1;self.bad();return 'bad-url',None
            if c=='\\':
                if self.valid_escape():out+=self.escape();continue
                self.i+=1;self.bad();return 'bad-url',None
            out+=c;self.i+=1
        return 'url',out
    def string(self):
        quote=self.peek();self.i+=1;out=''
        while self.peek() is not None:
            c=self.peek()
            if c==quote:self.i+=1;return 'string',out
            if c=='\n':return 'bad-string',out
            if c=='\\':
                if self.peek(1) is None:self.i+=1;continue
                if self.peek(1)=='\n':self.i+=2;continue
                out+=self.escape();continue
            out+=c;self.i+=1
        return 'string',out
    def next(self):
        c=self.peek();delegation=None
        if c is None:return None
        if c in WS:
            while self.peek() is not None and self.peek() in WS:self.i+=1
            kind,value='space',None
        elif c in '\"\'':kind,value=self.string()
        elif c==')':self.i+=1;kind,value='close',''
        elif c.isalpha() or c in '_-' or ord(c)>=128 or self.valid_escape():
            value=self.name();kind='ident'
            if self.peek()=='(':
                self.i+=1
                if value.lower()=='url':
                    opener_end=self.units[self.i-1][1]
                    whitespace_start=self.i
                    while self.peek() is not None and self.peek(1) is not None and self.peek() in WS and self.peek(1) in WS:self.i+=1
                    quoted=self.peek() in ['\"',"'"] or self.peek() in list(WS) and self.peek(1) in ['\"',"'"]
                    if quoted:
                        kind='function'
                        nline,ncolumn=metadata(self.source,opener_end)
                        delegation={'position':opener_end,'line':nline,'column':ncolumn,'spec_skipped_whitespace_units':self.i-whitespace_start}
                    else:kind,value=self.url()
                else:kind='function'
                if kind=='function' and value.lower()=='url':self.seen=True
        else:self.i+=1;kind,value='delim',c
        offset=self.units[self.i-1][1] if self.i else 0
        line,column=metadata(self.source,offset)
        return {'kind':kind,'value':value,'position':offset,'line':line,'column':column,'pending':kind=='function','seen':self.seen,'quoted_url_delegation':delegation}

def tokens(source):
    parser=Reference(source);out=[]
    while (token:=parser.next()) is not None:out.append(token)
    return out
