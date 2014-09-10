import bpy
from cam import simple
from cam.simple import *

def addTestCurve(loc):
		bpy.ops.curve.primitive_bezier_circle_add(radius=.05, view_align=False, enter_editmode=False, location=loc)
		bpy.ops.object.editmode_toggle()
		bpy.ops.curve.duplicate()
		bpy.ops.transform.resize(value=(0.5, 0.5, 0.5), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
		bpy.ops.curve.duplicate()
		bpy.ops.transform.resize(value=(0.5, 0.5, 0.5), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
		bpy.ops.object.editmode_toggle()

def addTestMesh(loc):
	bpy.ops.mesh.primitive_monkey_add(radius=.01, view_align=False, enter_editmode=False, location=loc)
	bpy.ops.transform.rotate(value=-1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=loc)
	bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False), constraint_orientation='GLOBAL')
	bpy.ops.transform.translate(value=(-0.01, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
	
	bpy.ops.object.editmode_toggle()

def deleteFirstVert(ob):
	activate(ob)
	bpy.ops.object.editmode_toggle()
	
	bpy.ops.mesh.select_all(action='DESELECT')


	bpy.ops.object.editmode_toggle()
	for i,v in enumerate(ob.data.vertices):
		v.select=False
		if i==0:
			v.select=True
	ob.data.update()
			
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.delete(type='VERT')
	bpy.ops.object.editmode_toggle()

def testCalc(o):
	bpy.ops.object.calculate_cam_path()
	deleteFirstVert(bpy.data.objects[o.path_object_name])
	
def testCutout(pos):
	addTestCurve((pos[0],pos[1],-.05))
	bpy.ops.scene.cam_operation_add()
	o=bpy.context.scene.cam_operations[-1]
	o.strategy = 'CUTOUT'
	testCalc(o)
	
def testPocket(pos):
	addTestCurve((pos[0],pos[1],-.01))
	bpy.ops.scene.cam_operation_add()
	o=bpy.context.scene.cam_operations[-1]
	o.strategy = 'POCKET'
	o.helix_enter = True
	o.retract_tangential=True
	testCalc(o)

def testParallel(pos):
	addTestMesh((pos[0],pos[1],-.02))
	bpy.ops.scene.cam_operation_add()
	o=bpy.context.scene.cam_operations[-1]
	o.ambient_behaviour='AROUND'
	o.material_radius_around_model=0.01
	bpy.ops.object.calculate_cam_path()

def testWaterline(pos):
	addTestMesh((pos[0],pos[1],-.02))
	bpy.ops.scene.cam_operation_add()
	o=bpy.context.scene.cam_operations[-1]
	o.strategy='WATERLINE'
	o.pixsize=.0002
	#o.ambient_behaviour='AROUND'
	#o.material_radius_around_model=0.01

	testCalc(o)
	#bpy.ops.object.cam_simulate()

		
def testSimulation():
	pass;

def cleanUp():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	while len(bpy.context.scene.cam_operations)>0:
		bpy.ops.scene.cam_operation_remove()

	
tests=[
		testCutout,
		testParallel,
		testWaterline,
		testPocket,
		
		]
		
cleanUp()

#deleteFirstVert(bpy.context.active_object)
for i,t in enumerate(tests):
	p=i*.2
	t((p,0,0))
#	cleanUp()


#cleanUp()
	
	