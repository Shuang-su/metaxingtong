p='/workspace/shared/ferris-cabin-build-20261030/scenes/ferris-wheel-cabin/scripts/strict_aperture_audit.py'
s=open(p).read();a=s.index(' def through_ring');b=s.index(' def allowed',a)
s=s[:a]+''' ring_cache={}
 for name,ps in rings.items():
  pairs=max(((a,b) for a in ps for b in ps),key=lambda ab:(ab[1].xy-ab[0].xy).length)
  u=Vector((pairs[1].x-pairs[0].x,pairs[1].y-pairs[0].y,0)).normalized();n=Vector((u.y,-u.x,0))
  ring_cache[name]=(ps[0],u,n,[(v.dot(u),v.z) for v in ps])
 def through_ring(name,origin,d):
  data=ring_cache.get(name)
  if data is None:return False
  p0,u,n,polygon=data;den=d.dot(n)
  if abs(den)<1e-10:return False
  t=(p0-origin).dot(n)/den
  if t<0:return False
  p=origin+d*t
  return inside((p.dot(u),p.z),polygon)
'''+s[b:];open(p,'w').write(s)
