import bpy

config = {}
config_fade_from_current_frame = {
    '1.120': [21050, 1],
    '1.174': [50720, 1],
}
config_fade_to_current_frame = {
    '1.002': [90, 1],
    '1.121': [21088, 1],
}


class CrossfadeOperator(bpy.types.Operator):
    bl_idname = 'wm.crossfade'
    bl_label = 'Crossfade'

    def execute(self, context):
        i = 0
        for left in bpy.context.sequences:
            if left.type != 'SOUND':
                continue
            fade_from_current_frame(left)
            fade_to_current_frame(left)
            for right in bpy.context.sequences:
                if right.type == 'SOUND' and \
                   left.channel != right.channel and \
                   left.frame_final_end > right.frame_final_start and \
                   right.frame_final_start > left.frame_final_start:
                    # bpy.ops.sequencer.crossfade_sounds() работает с ошибками. Не использовать.
                    fade_left(left, right)
                    fade_right(left, right)
                    i += 1
                    print(i, left, right)
                    break
        return {'FINISHED'}


class CrossfadePanel(bpy.types.Panel):
    bl_category = 'Tools'
    bl_context = 'object'
    bl_idname = 'OBJECT_PT_crossfade'
    bl_label = 'Crossfade'
    bl_region_type = 'UI'
    bl_space_type = 'SEQUENCE_EDITOR'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('wm.crossfade')


def fade_current_frame(left, config, frame_volume_0):
    bpy.context.scene.frame_current = config[0]
    left.volume = config[1]
    left.keyframe_insert('volume')
    bpy.context.scene.frame_current = frame_volume_0
    left.volume = 0
    left.keyframe_insert('volume')


def fade_from_current_frame(left):
    if left.name not in config_fade_from_current_frame:
        return
    fade_current_frame(left, config_fade_from_current_frame[left.name], frame_volume_0=left.frame_final_end)


def fade_to_current_frame(left):
    if left.name not in config_fade_to_current_frame:
        return
    fade_current_frame(left, config_fade_to_current_frame[left.name], frame_volume_0=left.frame_final_start)


def fade_left(left, right):
    bpy.context.scene.frame_current = right.frame_final_start
    if left.name in config:
        left.volume = config[left.name][1]
    else:
        left.volume = 1
    left.keyframe_insert('volume')
    bpy.context.scene.frame_current = left.frame_final_end
    left.volume = 0
    left.keyframe_insert('volume')


def fade_right(left, right):
    bpy.context.scene.frame_current = right.frame_final_start
    right.volume = 0
    right.keyframe_insert('volume')
    bpy.context.scene.frame_current = left.frame_final_end
    if right.name in config:
        right.volume = config[right.name][0]
    else:
        right.volume = 1
    right.keyframe_insert('volume')


def register():
    bpy.utils.register_class(CrossfadeOperator)
    bpy.utils.register_class(CrossfadePanel)


def unregister():
    bpy.utils.unregister_class(CrossfadeOperator)
    bpy.utils.unregister_class(CrossfadePanel)


if __name__ == '__main__':
    register()
