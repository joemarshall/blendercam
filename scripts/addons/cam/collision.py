import bpy
import time

from cam import simple
from cam.simple import *

BULLET_SCALE=1000 # this is a constant for scaling the rigidbody collision world for higher precision from bullet library

#
def getCutterBullet(o):
	'''cutter for rigidbody simulation collisions
		note that everything is 100x bigger for simulation precision.'''
	s=bpy.context.scene
	if s.objects.get('cutter')!= None:
		c=s.objects['cutter']
		activate(c)

	type=o.cutter_type
	if type=='END':
		bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=BULLET_SCALE*o.cutter_diameter/2, depth=BULLET_SCALE*o.cutter_diameter, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'CYLINDER'
	elif type=='BALL':
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=BULLET_SCALE*o.cutter_diameter/2, view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'SPHERE'
	elif type=='VCARVE':
		
		angle=o.cutter_tip_angle
		s=math.tan(math.pi*(90-angle/2)/180)/2
		bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=BULLET_SCALE*o.cutter_diameter/2, radius2=0, depth = BULLET_SCALE*o.cutter_diameter*s, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(math.pi, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'CONE'
	cutter.name='cam_cutter'	
	o.cutter_shape=cutter
	return cutter

#
def prepareBulletCollision(o):
	'''prepares all objects needed for sampling with bullet collision'''
	progress('preparing collisions')
	t=time.time()
	s=bpy.context.scene
	s.gravity=(0,0,0)
	#cleanup rigidbodies wrongly placed somewhere in the scene
	for ob in bpy.context.scene.objects:
		if ob.rigid_body != None and (bpy.data.groups.find('machine')>-1 and ob.name not in bpy.data.groups['machine'].objects):
			activate(ob)
			bpy.ops.rigidbody.object_remove()
			
	for collisionob in o.objects:
		activate(collisionob)
		bpy.ops.object.duplicate(linked=False)
		if collisionob.type=='CURVE' or collisionob.type=='FONT':#support for curve objects collision
			bpy.ops.object.convert(target='MESH', keep_original=False)

		collisionob=bpy.context.active_object
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		collisionob.rigid_body.collision_shape = 'MESH'
		collisionob.rigid_body.collision_margin = o.skin*BULLET_SCALE
		bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
		collisionob.location=collisionob.location*BULLET_SCALE
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
	
	getCutterBullet(o)
	
	#machine objects scaling up to simulation scale
	if bpy.data.groups.find('machine')>-1:
		for ob in bpy.data.groups['machine'].objects:
			activate(ob)
			bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
			ob.location=ob.location*BULLET_SCALE
	#stepping simulation so that objects are up to date
	bpy.context.scene.frame_set(0)
	bpy.context.scene.frame_set(1)
	bpy.context.scene.frame_set(2)
	progress(time.time()-t)
	
	
def cleanupBulletCollision(o):
	if bpy.data.groups.find('machine')>-1:
		machinepresent=True
	else:
		machinepresent=False
	for ob in bpy.context.scene.objects:
		if ob.rigid_body != None and not (machinepresent and ob.name in bpy.data.groups['machine'].objects):
			delob(ob)
	#machine objects scaling up to simulation scale
	if machinepresent:
		for ob in bpy.data.groups['machine'].objects:
			activate(ob)
			bpy.ops.transform.resize(value=(1.0/BULLET_SCALE, 1.0/BULLET_SCALE, 1.0/BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
			ob.location=ob.location/BULLET_SCALE