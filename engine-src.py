import json,os,sys,urllib.request,urllib.error
# colour: white 0 black 1; piece=(col<<3)|type. Types p,n,b,r,q,k.
P,N,B,R,Q,K=1,2,3,4,5,6
WT={"p":P,"n":N,"b":B,"r":R,"q":Q,"k":K}
VA={P:100,N:320,B:330,R:500,Q:900,K:10000}
F="abcdefgh"
def sq(f,r):return r*8+f
PP=[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0]
PN=[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
PB=[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
PR=[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
PQ=[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
PK=[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
PT={P:PP,N:PN,B:PB,R:PR,Q:PQ,K:PK}

class B:
 def __init__(s):
  s.p=[0]*64;s.c=0;s.ca=0;s.ep=-1;s.h=0;s.m=1
 def cp(s):
  q=B();q.p=s.p[:];q.c=s.c;q.ca=s.ca;q.ep=s.ep;q.h=s.h;q.m=s.m;return q
 @staticmethod
 def fen(fen):
  b=B();pt=fen.split();rows=pt[0].split("/")
  for r,row in enumerate(rows):
   rk=7-r;fl=0
   for ch in row:
    if ch.isdigit():fl+=int(ch)
    else:
     col=0 if ch.isupper() else 1
     b.p[sq(fl,rk)]=(col<<3)|WT[ch.lower()];fl+=1
  b.c=0 if pt[1]=="w" else 1
  if len(pt)>2:
   b.ca=0
   if "K" in pt[2]:b.ca|=1
   if "Q" in pt[2]:b.ca|=2
   if "k" in pt[2]:b.ca|=4
   if "q" in pt[2]:b.ca|=8
   b.ep=-1 if pt[3]=="-" else F.index(pt[3][0])+(int(pt[3][1])-1)*8
  if len(pt)>4:b.h=int(pt[4])
  if len(pt)>5:b.m=int(pt[5])
  return b
 def king(s,col):
  for i,x in enumerate(s.p):
   if x==(col<<3)|K:return i
  return -1
 def attacked(s,sq_,by):
  f,r=sq_%8,sq_//8
  if by==0:
   for df in(-1,1):
    f2,r2=f+df,r-1
    if 0<=f2<8 and 0<=r2<8 and s.p[sq(f2,r2)]==P:return 1
  else:
   for df in(-1,1):
    f2,r2=f+df,r+1
    if 0<=f2<8 and 0<=r2<8 and s.p[sq(f2,r2)]==(1<<3)|P:return 1
  for df,dr in((1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)):
   f2,r2=f+df,r+dr
   if 0<=f2<8 and 0<=r2<8 and s.p[sq(f2,r2)]==(by<<3)|N:return 1
  for df in(-1,0,1):
   for dr in(-1,0,1):
    if df==0 and dr==0:continue
    f2,r2=f+df,r+dr
    if 0<=f2<8 and 0<=r2<8 and s.p[sq(f2,r2)]==(by<<3)|K:return 1
  for df,dr in((1,1),(1,-1),(-1,1),(-1,-1)):
   f2,r2=f+df,r+dr
   while 0<=f2<8 and 0<=r2<8:
    x=s.p[sq(f2,r2)]
    if x:
     if x>>3==by and(x&7)in(B,Q):return 1
     break
    f2+=df;r2+=dr
  for df,dr in((1,0),(-1,0),(0,1),(0,-1)):
   f2,r2=f+df,r+dr
   while 0<=f2<8 and 0<=r2<8:
    x=s.p[sq(f2,r2)]
    if x:
     if x>>3==by and(x&7)in(R,Q):return 1
     break
    f2+=df;r2+=dr
  return 0
 def check(s,col):return s.attacked(s.king(col),col^1)
 def own(s,x,col):return x and x>>3==col
 def foe(s,x,col):return x and x>>3!=col
 def gen(s):
  mv=[];col=s.c
  for i,x in enumerate(s.p):
   if not x or x>>3!=col:continue
   t=x&7;f,r=i%8,i//8
   if t==P:s.pawn(i,f,r,col,mv)
   elif t==N:
    for df,dr in((1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)):
     f2,r2=f+df,r+dr
     if 0<=f2<8 and 0<=r2<8:
      j=sq(f2,r2)
      if not s.own(s.p[j],col):mv.append((i,j,0))
   elif t in(B,R,Q):
    ds=[]
    if t in(B,Q):ds+=[(1,1),(1,-1),(-1,1),(-1,-1)]
    if t in(R,Q):ds+=[(1,0),(-1,0),(0,1),(0,-1)]
    for df,dr in ds:
     f2,r2=f+df,r+dr
     while 0<=f2<8 and 0<=r2<8:
      j=sq(f2,r2);y=s.p[j]
      if not y:mv.append((i,j,0))
      else:
       if s.foe(y,col):mv.append((i,j,0))
       break
      f2+=df;r2+=dr
   elif t==K:
    for df in(-1,0,1):
     for dr in(-1,0,1):
      if df==0 and dr==0:continue
      f2,r2=f+df,r+dr
      if 0<=f2<8 and 0<=r2<8:
       j=sq(f2,r2)
       if not s.own(s.p[j],col):mv.append((i,j,0))
    s.castle(i,col,mv)
  return mv
 def pawn(s,i,f,r,col,mv):
  d=1 if col==0 else -1;st=1 if col==0 else 6;pr=7 if col==0 else 0;r2=r+d
  if 0<=r2<8 and not s.p[sq(f,r2)]:
   s.ppush(i,sq(f,r2),pr,mv)
   if r==st and not s.p[sq(f,r+2*d)]:mv.append((i,sq(f,r+2*d),0))
  for df in(-1,1):
   f2,r2=f+df,r+d
   if 0<=f2<8 and 0<=r2<8:
    j=sq(f2,r2);y=s.p[j]
    if s.foe(y,col):s.ppush(i,j,pr,mv)
    elif j==s.ep:mv.append((i,j,0))
 def ppush(s,i,j,pr,mv):
  if j//8==pr:
   for q in("q","r","b","n"):mv.append((i,j,q))
  else:mv.append((i,j,0))
 def castle(s,i,col,mv):
  row=0 if col==0 else 7
  if i!=sq(4,row):return
  foe=col^1;ks=1 if col==0 else 4;qs=2 if col==0 else 8
  if s.ca&ks and not s.p[sq(5,row)] and not s.p[sq(6,row)] and s.p[sq(7,row)]==(col<<3)|R and not s.attacked(i,foe) and not s.attacked(sq(5,row),foe) and not s.attacked(sq(6,row),foe):mv.append((i,sq(6,row),0))
  if s.ca&qs and not s.p[sq(3,row)] and not s.p[sq(2,row)] and not s.p[sq(1,row)] and s.p[sq(0,row)]==(col<<3)|R and not s.attacked(i,foe) and not s.attacked(sq(3,row),foe) and not s.attacked(sq(2,row),foe):mv.append((i,sq(2,row),0))
 def apply(s,m):
  i,j,pr=m;col=s.c;x=s.p[i];t=x&7
  if t==P and j==s.ep and not s.p[j]:s.p[sq(j%8,i//8)]=0
  if t==K and abs(j%8-i%8)==2:
   if j%8==6:s.p[sq(7,j//8)]=0;s.p[sq(5,j//8)]=(col<<3)|R
   else:s.p[sq(0,j//8)]=0;s.p[sq(3,j//8)]=(col<<3)|R
  if t==K:s.ca&=~3 if col==0 else ~12
  for rm,bit in((sq(0,0),2),(sq(7,0),1),(sq(0,7),8),(sq(7,7),4)):
   if i==rm or j==rm:s.ca&=~bit
  s.ep=-1
  if t==P and abs(j//8-i//8)==2:s.ep=sq(i%8,(i//8+j//8)//2)
  s.h=0 if(t==P or s.p[j])else s.h+1
  s.p[i]=0
  if pr:
   pt={"q":Q,"r":R,"b":B,"n":N}[pr];s.p[j]=(col<<3)|pt
  else:s.p[j]=x
  s.c=col^1
  if col==1:s.m+=1
 def legal(s):
  o=[]
  for m in s.gen():
   q=s.cp();q.apply(m)
   if not q.check(s.c):o.append(m)
  return o
 def eval(s):
  v=0
  for i,x in enumerate(s.p):
   if not x:continue
   col=x>>3;t=x&7;w=VA[t]+PT[t][i if col==0 else 63-i]
   v+=w if col==0 else -w
  return v
 def uci(s,m):
  i,j,pr=m;u=F[i%8]+str(i//8+1)+F[j%8]+str(j//8+1)
  return u+pr if pr else u
 def parse(s,u):
  i=F.index(u[0])+(int(u[1])-1)*8;j=F.index(u[2])+(int(u[3])-1)*8
  return(i,j,u[4] if len(u)==5 else 0)

def order(b,mv):
 col=b.c
 def sc(m):
  i,j,pr=m;y=b.p[j]
  if y:return 10*VA[y&7]-VA[b.p[i]&7]
  if pr:return 900
  return 0
 return sorted(mv,key=sc,reverse=True)

def search(b,d,a,bt,n):
 n[0]+=1
 if d==0:return b.eval()
 mv=b.legal()
 if not mv:return -100000+b.m if b.check(b.c) else 0
 if b.c==0:
  best=-10**9
  for m in order(b,mv):
   q=b.cp();q.apply(m);v=search(q,d-1,a,bt,n)
   if v>best:best=v
   if best>a:a=best
   if a>=bt:break
  return best
 best=10**9
 for m in order(b,mv):
  q=b.cp();q.apply(m);v=search(q,d-1,a,bt,n)
  if v<best:best=v
  if best<bt:bt=best
  if a>=bt:break
 return best

def choose(b,d):
 mv=b.legal()
 if not mv:return None
 n=[0];col=b.c;best=None;bv=-10**9 if col==0 else 10**9;a,bt=-10**9,10**9
 for m in order(b,mv):
  q=b.cp();q.apply(m);v=search(q,d-1,a,bt,n)
  if col==0:
   if v>bv:bv,best=v,m
   if bv>a:a=bv
  else:
   if v<bv:bv,best=v,m
   if bv<bt:bt=bv
 return best

ENV=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("MAKEFUN_ENV_URL is not set")
DEPTH=int(os.environ.get("MAKEFUN_DEPTH")or 4)
def post(path,body):
 req=urllib.request.Request(ENV+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
 try:
  with urllib.request.urlopen(req) as r:return json.load(r)
 except urllib.error.HTTPError as e:
  sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")

while True:
 g=post("/game",{})
 if g["status"]=="done":break
 while g["status"]=="your_move":
  b=B.fen(g["fen"])
  if g["colour"]=="black":b.c=1
  m=choose(b,DEPTH)
  u=b.uci(m) if m else g["legal_moves"][0]
  g=post("/move",{"game":g["game"],"move":u})
 print(f"game {g['game']}: {g['outcome']} {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')}W {g.get('draws')}D {g.get('losses')}L",file=sys.stderr)
