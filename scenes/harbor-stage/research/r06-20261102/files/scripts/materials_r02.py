# One globally selected teal preview-like state, never changed per camera.
def material(name,color,metal=0,rough=.4,emission=0,imagefile=None,transmission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;bs.inputs['Transmission Weight'].default_value=transmission
    if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    if imagefile:
        im=bpy.data.images.load(str(R/'textures'/imagefile));im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        if emission:m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color'])
    return m
materials={
 'metal':material('Titanium brushed',(.19,.23,.29),.72,.24),
 'navy':material('Navy structure',(.014,.028,.068),.62,.24),
 'stage':material('Reflective stage',(.024,.04,.07),.72,.16),
 'emission':material('Teal edge emitter',(.04,.83,.95),.15,.3,2.8),
 'pink_emission':material('Pink accessory neon',(.75,.07,.35),.15,.3,2.5),
 'chrome':material('Chrome circle inserts',(.67,.73,.82),.98,.13),
 'display':material('2025 circular LED signage',(.02,.55,.66),.2,.32,1.2,'display-teal-2025.png'),
 'grid':material('Curved support grid LED',(.07,.18,.27),.5,.3,.5,'curved-band-led-grid.png'),
 'sand':material('Sand',(.55,.35,.16),0,.9),
 'water':material('Sea',(.025,.24,.31),.55,.23),
 'hill':material('Unmeasured distant hill',(.09,.22,.035),0,.95),
 'leaf':material('Palm leaves',(.23,.36,.035),0,.63),
 'bark':material('Palm trunk',(.33,.20,.08),0,.83),
 'tower':material('Lighthouse ivory',(.75,.70,.55),.05,.7),
 'glass':material('Dark blue glazing',(.035,.15,.21),.3,.12,transmission=.25),
 'boat':material('White hull',(.76,.8,.77),.15,.32),
 'sail':material('Canvas sail',(.72,.67,.46),0,.8),
 'umbrella_purple':material('Purple parasol',(.31,.12,.55),0,.48),
 'umbrella_pink':material('Pink parasol',(.65,.10,.28),0,.48),
 'purple':material('Purple beach accessory',(.32,.09,.47),.3,.32),
 'pink':material('Pink beach accessory',(.75,.08,.24),.3,.32),
 'teal':material('Teal beach accessory',(.03,.5,.4),.3,.32),
}
def uv_default(ob):
    uv=ob.data.uv_layers.new(name='UVMap') if not ob.data.uv_layers else ob.data.uv_layers.active
    vv=ob.data.vertices;name=ob.name
    for face in ob.data.polygons:
        for li in face.loop_indices:
            vi=ob.data.loops[li].vertex_index;co=vv[vi].co
            if name.startswith('FRAME_') and name in ('FRAME_L','FRAME_R'):
                p=vi%4;u=float(p in (1,3));v=(vi//4)/64
            elif name.startswith('CROWN_') and ('DISPLAY' in name):
                u=(math.atan2(co.y-1,co.x)/math.tau)%1;v=(co.z-min(v.co.z for v in vv))/(max(v.co.z for v in vv)-min(v.co.z for v in vv))
            else:u=co.x*.1;v=co.z*.1
            uv.data[li].uv=(u,v)
for ob in [o for o in sc.objects if o.type=='MESH']:
    surface=ob.get('surface')
    if not surface:
        n=ob.name
        surface='metal'
        if n=='PLATFORM_MAIN':surface='stage'
        elif n.startswith('PLATFORM') or n.startswith('STAIR') or n.startswith('OUTER_'):surface='navy'
        elif 'TRIM' in n or n=='CROWN_LOWER_LIP':surface='emission'
        elif 'DISPLAY' in n:surface='display'
    ob.data.materials.clear();ob.data.materials.append(materials[surface]);uv_default(ob)
    if ob.name in ('FRAME_L','FRAME_R'):
        ob.data.materials.append(materials['grid'])
        for p in ob.data.polygons:
            if p.index>=2 and (p.index-2)%4==0:p.material_index=1
    if ob.name.startswith('CHEVRON_') and not ob.name.startswith(('CHEVRON_LIGHT','CHEVRON_RING')):
        ob.data.materials[0]=materials['navy']
    ob['material_state']='TEAL_PREVIEW_CONDITIONAL_SHARED_ALL_CAMERAS'
sc['material_state']='Teal preview-like global state based on BV1uqYvzDEZK5.051975; not an exact reproduction of other lighting times'
sc['residuals']='No volumetric moving beams/crowds/broadcast typography; large mascots and complete environment still pending; hidden structures inferred'
