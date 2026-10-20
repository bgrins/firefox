import json
from generate import generate
MAX=(1<<31)-1
MIN=-(1<<31)
RECTS=[[0,0,10,20],[MAX,0,0,1],[MAX,0,1,1],[MIN,0,-1,1],
       [0,MAX,1,1],[0,MIN,1,-1],[MAX,MIN,-1,1],[0,0,-5,-7]]
PAIRS=[[[5,2,8,6],[0,0,3,10]],[[3,2,8,6],[0,0,3,10]],
       [[2,5,6,8],[0,0,10,3]],[[0,0,0,0],[5,0,3,10]],
       [[1,2,4,6],[0,0,10,10]],[[20,20,30,30],[0,0,10,10]]]
ENDPOINTS=[[20,4,10,3],[0,0,0,0],[0,0,0,-5],[0,-5,0,0]]

def rows():
    result=[]
    for i,(x,y,w,h) in enumerate(RECTS):
        b=[x,y,x+w,y+h] if MIN<=x+w<=MAX and MIN<=y+h<=MAX else [0]*4
        result.append([0,i,*b])
    for i,(a,b) in enumerate(PAIRS):
        q=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        if q[2]<q[0] or q[3]<q[1]:q[2:]=q[:2]
        final=q[:]
        if q[2]<=q[0] or q[3]<=q[1]:
            for j in [0,1]:
                width=min(b[j+2]-b[j],q[j+2]-q[j])
                near=min(max(b[j],q[j])+width,b[j+2])-width
                final[j]=near;final[j+2]=near+width
        result.append([1,i,*q,*final])
    for i,(sa,sm,ea,em) in enumerate(ENDPOINTS):
        for x in [ea-1,ea,ea+1,sa-1,sa,sa+1]:
            e=x-em if em and x<=ea else x+sm if sm and x>sa else x
            l=x-em if em and x<ea else x+sm if sm and x>=sa else x
            result.append([2,i,x,e,l])
    return result

def source():
    prefix=generate('combined','mode_driver.cpp')
    prefix=prefix[:prefix.index('int main(')]
    code=['void emitBox(const nsRectAbsolute& b){std::cout<<","<<b.X()<<","<<b.Y()<<","<<b.XMost()<<","<<b.YMost();}', 'int main(){']
    for i,r in enumerate(RECTS):
        code.append(' {nsRect r{'+','.join(map(str,r))+'};auto b=nsRectAbsolute::FromRect(r);std::cout<<"[0,'+str(i)+'";emitBox(b);std::cout<<"]\\n";}')
    for i,(a,b) in enumerate(PAIRS):
        code.append(' {nsRectAbsolute a{'+','.join(map(str,a))+'},b{'+','.join(map(str,b))+'};auto q=a.Intersect(b);auto f=q.IsEmpty()?q.MoveInsideAndClamp(b):q;std::cout<<"[1,'+str(i)+'";emitBox(q);emitBox(f);std::cout<<"]\\n";}')
    for i,(sa,sm,ea,em) in enumerate(ENDPOINTS):
        for x in [ea-1,ea,ea+1,sa-1,sa,sa+1]:
            code.append(' {mozilla::dom::ViewTimeline::StickyDisplacement d{'+','.join(map(str,[sa,sm,ea,em]))+'};std::cout<<"[2,'+str(i)+','+str(x)+',"<<d.Earliest('+str(x)+')<<","<<d.Latest('+str(x)+')<<"]\\n";}')
    code.append('}')
    return prefix+'\n'.join(code)+'\n'
