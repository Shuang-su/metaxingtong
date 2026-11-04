"""Float64 (Python float) triangle distance by feature pairs and edge/face intersections."""
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def add(a,b):return tuple(a[i]+b[i] for i in range(3))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(a[i]*b[i] for i in range(3))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length2(a):return dot(a,a)
def clamp(x):return min(1.0,max(0.0,x))

def point_triangle2(p,a,b,c):
    ab=sub(b,a);ac=sub(c,a);ap=sub(p,a);d1=dot(ab,ap);d2=dot(ac,ap)
    if d1<=0 and d2<=0:return length2(ap)
    bp=sub(p,b);d3=dot(ab,bp);d4=dot(ac,bp)
    if d3>=0 and d4<=d3:return length2(bp)
    vc=d1*d4-d3*d2
    if vc<=0 and d1>=0 and d3<=0:return length2(sub(p,add(a,mul(ab,d1/(d1-d3)))))
    cp=sub(p,c);d5=dot(ab,cp);d6=dot(ac,cp)
    if d6>=0 and d5<=d6:return length2(cp)
    vb=d5*d2-d1*d6
    if vb<=0 and d2>=0 and d6<=0:return length2(sub(p,add(a,mul(ac,d2/(d2-d6)))))
    va=d3*d6-d5*d4
    if va<=0 and (d4-d3)>=0 and (d5-d6)>=0:
        return length2(sub(p,add(b,mul(sub(c,b),(d4-d3)/((d4-d3)+(d5-d6))))))
    denom=va+vb+vc
    if abs(denom)<1e-30:raise ValueError('Degenerate triangle')
    q=add(a,add(mul(ab,vb/denom),mul(ac,vc/denom)))
    return length2(sub(p,q))

def segment_segment2(p1,q1,p2,q2):
    d1=sub(q1,p1);d2=sub(q2,p2);r=sub(p1,p2);a=dot(d1,d1);e=dot(d2,d2);f=dot(d2,r)
    if a<1e-30 and e<1e-30:return length2(r)
    if a<1e-30:s=0.;t=clamp(f/e)
    else:
        c=dot(d1,r)
        if e<1e-30:t=0.;s=clamp(-c/a)
        else:
            b=dot(d1,d2);denom=a*e-b*b;s=clamp((b*f-c*e)/denom) if denom>1e-30 else 0.
            t=(b*s+f)/e
            if t<0:t=0.;s=clamp(-c/a)
            elif t>1:t=1.;s=clamp((b-c)/a)
    return length2(sub(add(p1,mul(d1,s)),add(p2,mul(d2,t))))

def segment_hits_triangle(p,q,a,b,c):
    d=sub(q,p);e1=sub(b,a);e2=sub(c,a);h=cross(d,e2);det=dot(e1,h)
    if abs(det)<1e-18:return False
    v=sub(p,a);u=dot(v,h)/det
    if u < -1e-12 or u > 1+1e-12:return False
    k=cross(v,e1);w=dot(d,k)/det
    if w < -1e-12 or u+w > 1+1e-12:return False
    t=dot(e2,k)/det
    return -1e-12<=t<=1+1e-12

def triangle_triangle2(a,b):
    ae=[(a[i],a[(i+1)%3]) for i in range(3)];be=[(b[i],b[(i+1)%3]) for i in range(3)]
    if any(segment_hits_triangle(p,q,*b) for p,q in ae) or any(segment_hits_triangle(p,q,*a) for p,q in be):return 0.
    return max(0.,min([point_triangle2(p,*b) for p in a]+[point_triangle2(p,*a) for p in b]+[
        segment_segment2(p,q,r,s) for p,q in ae for r,s in be]))

def tests():
    import math
    a=((0.,0.,0.),(1.,0.,0.),(0.,1.,0.))
    cases=[('parallel_gap',a,tuple((x,y,.25) for x,y,z in a),.25),
        ('coplanar_overlap',a,((.1,.1,0.),(.2,.1,0.),(.1,.2,0.)),0.),
        ('edge_through_face',a,((.2,.2,-1.),(.2,.2,1.),(.8,.2,1.)),0.),
        ('separate_parallel',a,((2.,0.,0.),(3.,0.,0.),(2.,1.,0.)),1.)]
    rows=[]
    for name,x,y,expected in cases:
        d=math.sqrt(triangle_triangle2(x,y));dr=math.sqrt(triangle_triangle2(y,x));assert abs(d-expected)<1e-12 and abs(d-dr)<1e-12
        rows.append(dict(name=name,distance=d,expected=expected,symmetry_error=abs(d-dr)))
    return rows
