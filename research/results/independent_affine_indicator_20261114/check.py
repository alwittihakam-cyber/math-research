"""Independent finite check of one-hot affine-indicator coverage.
Setting from Kamil Braun/Noemesis lem:affine-indicator-kernel (17 Oct 2026).
No imported executable code. Exact F2 elimination with Python integer bitsets.
"""
import itertools,random,json,time

def rank(rows):
 b={}
 for v in rows:
  while v:
   p=v.bit_length()-1
   if p in b:v^=b[p]
   else:b[p]=v;break
 return len(b)

def run(s=4,k=2,trials=1000):
 assert k == 2 and trials > 0
 points=list(itertools.product(range(3),repeat=s)); N=len(points); full=(1<<N)-1
 bits=[sum((1<<(2*i+(v-1))) for i,v in enumerate(p) if v) for p in points]
 mono=[0]+[sum(1<<(2*i+a) for i,a in zip(I,A)) for d in range(1,k+1) for I in itertools.combinations(range(s),d) for A in itertools.product(range(2),repeat=d)]
 rows=[sum(1<<j for j,m in enumerate(mono) if b&m==m) for b in bits]
 half=[sum(1<<i for i,b in enumerate(bits) if (b&m).bit_count()%2==1) for m in range(1,1<<(2*s))]
 aff={full}
 for h in half:aff|={h,full^h}
 for i,a in enumerate(half):
  for b in half[i+1:]:
   aff.update((a&b,a&(full^b),(full^a)&b,(full^a)&(full^b)))
 aff.discard(0);aff=list(aff)
 z=[]
 for m in range(1,1<<s):
  v=0
  for j,p in enumerate(points):
   x=sum(1 for i in range(s) if m>>i&1 and p[i]==1)%2
   y=sum(1 for i in range(s) if m>>i&1 and p[i]==2)%2
   c=1^(m.bit_count()%2)
   if x==y==c:v|=1<<j
  z.append(v)
 rng=random.Random(20261114); counts={}; witnesses=[]
 for t in range(trials):
  M=rng.choice((2,3,4)); arity=rng.choice((2,3)); mats=[]; Z=full
  for _ in range(M):
   ms=rng.sample(range(1,1<<s),arity);mats.append(ms); zz=0
   for m in ms:zz|=z[m-1]
   Z&=zz
  dim=len(mono)-rank(rows[i] for i in range(N) if not(Z>>i&1))
  if not dim:continue
  candidates=[a for a in aff if a&Z==a]
  span=rank(candidates)
  assert span <= dim
  key=f'kernel={dim},affine_span={span}'
  counts[key]=counts.get(key,0)+1
  if span<dim:witnesses.append({'s':s,'k':k,'rows':mats,'kernel_dim':dim,'affine_span':span,'Z':str(Z)})
  if not candidates:
   print('COUNTEREXAMPLE',witnesses[-1]);break
 return {'s':s,'k':k,'trials':t+1,'affine_sets':len(aff),'nonzero_kernel_counts':counts,'span_failures':witnesses[:5]}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--pairs',type=int,choices=(2,3,4,5),default=4);ap.add_argument('--trials',type=int,default=1000);a=ap.parse_args()
 start=time.monotonic(); r=run(a.pairs,2,a.trials);r['seconds']=time.monotonic()-start;print(json.dumps(r,indent=2))
