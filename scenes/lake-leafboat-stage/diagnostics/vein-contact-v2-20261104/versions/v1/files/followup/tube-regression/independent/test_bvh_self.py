from mathutils.bvhtree import BVHTree
v=[(-1,-1,0),(1,-1,0),(0,1,0),(0,-.5,-1),(0,-.5,1),(0,.5,0)];f=[(0,1,2),(3,4,5)];a=BVHTree.FromPolygons(v,f,all_triangles=True);b=BVHTree.FromPolygons(v,f,all_triangles=True);print('SAME_TREE',a.overlap(a));print('CLONE_TREE',a.overlap(b))
