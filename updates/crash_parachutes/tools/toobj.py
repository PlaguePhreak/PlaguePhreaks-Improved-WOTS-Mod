# Converts the reviewed FBX files into the game files the mod reads: OBJ (metres, Y up, facing +Z after the mod's x flip) + PNG.
import bpy, sys, os, shutil
a=sys.argv[sys.argv.index('--')+1:]; src,out,kind=a[0],a[1],a[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
ms=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in bpy.context.scene.objects:
    if o.type!='MESH': o.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active=ms[0]
# bake parents/scale into the vertices
for o in ms:
    mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
if len(ms)>1: bpy.ops.object.join()
o=bpy.context.active_object
if kind=='canopy':   # pivot at the riser top, 1.1 m above the harness
    for v in o.data.vertices: v.co.z-=1.1
# save the texture next to it
for m in o.data.materials:
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                n.image.filepath_raw=os.path.splitext(out)[0]+'.png'; n.image.file_format='PNG'; n.image.save(); break
bpy.ops.wm.obj_export(filepath=out, forward_axis='NEGATIVE_Z', up_axis='Y', export_selected_objects=True, export_materials=False,
                      export_triangulated_mesh=True, export_normals=True, export_uv=True)
print('ok',out,len(o.data.vertices))
