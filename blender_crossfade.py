import json

import bpy

crossfade_ignored_channels = []
fade_in = {}
fade_out = {}
volume_levels = {}
volume_levels_by_keyframes = {}
volume_levels_by_name = {}


class CountKeyframesOperator(bpy.types.Operator):
    bl_idname = 'wm.count_keyframes'
    bl_label = 'Count Keyframes'

    def execute(self, context):
        context.scene.frame_current = 0
        total = 0
        while True:
            r = bpy.ops.screen.keyframe_jump(next=True)
            if r == {'FINISHED'}:
                total += 1
                print(total, context.scene.frame_current)
            else:
                break
        return {'FINISHED'}


class CrossfadeOperator(bpy.types.Operator):
    bl_idname = 'wm.crossfade'
    bl_label = 'Crossfade'

    def execute(self, context):
        global volume_levels
        volume_levels = {}
        load_json_config()
        i = 0
        for left in context.sequences:
            if left.type != 'SOUND':
                continue
            if left not in volume_levels:
                volume_levels[left] = {}
            set_fade_in(left)
            set_fade_out(left)
            set_volume_levels_by_keyframes(left)
            set_volume_levels_by_name(left)
            for right in context.sequences:
                if is_crossfade(left, right):
                    # bpy.ops.sequencer.crossfade_sounds() работает с ошибками. Не использовать.
                    if right not in volume_levels:
                        volume_levels[right] = {}
                    fade_left(left, right)
                    fade_right(left, right)
                    i += 1
                    print(i, left, right)
                    break
        set_volume_levels()
        return {'FINISHED'}


class CrossfadePanel(bpy.types.Panel):
    bl_category = 'Tools'
    bl_context = 'object'
    bl_idname = 'OBJECT_PT_crossfade'
    bl_label = 'Tools'
    bl_region_type = 'UI'
    bl_space_type = 'SEQUENCE_EDITOR'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('wm.count_keyframes')
        row = layout.row()
        row.operator('wm.crossfade')
        split = layout.split(factor=0.7)
        column1 = split.column()
        column2 = split.column()
        column1.operator('wm.set_crossfade_frames')
        column2.prop(context.scene, 'crossfade_frames', text='')


class SetCrossfadeFramesOperator(bpy.types.Operator):
    bl_idname = 'wm.set_crossfade_frames'
    bl_label = 'Set Crossfade Frames'

    def execute(self, context):
        for strip in context.sequences:
            if not strip.select:
                continue
            delta_left = context.scene.frame_current - strip.frame_final_start
            delta_right = strip.frame_final_end - context.scene.frame_current
            cff = context.scene.crossfade_frames
            if delta_left > delta_right:
                if delta_right > cff:
                    strip.frame_final_duration -= delta_right - cff
                elif delta_right < cff:
                    strip.frame_final_duration += cff - delta_right
            elif delta_left < delta_right:
                if delta_left > cff:
                    strip.frame_offset_start += delta_left - cff
                elif delta_left < cff:
                    strip.frame_offset_start -= cff - delta_left
            break
        return {'FINISHED'}


def fade_left(left, right):
    for name, volume in volume_levels_by_name.items():
        if left.name.startswith(name):
            break
    else:
        volume = 1
    volume_levels[left][right.frame_final_start] = volume
    volume_levels[left][left.frame_final_end] = 0


def fade_right(left, right):
    for name, volume in volume_levels_by_name.items():
        if right.name.startswith(name):
            break
    else:
        volume = 1
    volume_levels[right][right.frame_final_start] = 0
    volume_levels[right][left.frame_final_end] = volume


def is_crossfade(left, right):
    if right.type == 'SOUND' and \
       right.channel != left.channel and \
       right.channel not in crossfade_ignored_channels and \
       left.channel not in crossfade_ignored_channels and \
       left.frame_final_end > right.frame_final_start and \
       right.frame_final_start > left.frame_final_start and \
       right.frame_final_end > left.frame_final_end:
        return True
    else:
        return False


def load_json_config():
    global crossfade_ignored_channels, fade_out, fade_in, volume_levels_by_keyframes, volume_levels_by_name
    path = bpy.path.abspath('//config.json')
    try:
        with open(path) as f:
            data = json.load(f)
            crossfade_ignored_channels = data.get('crossfade_ignored_channels', [])
            fade_in = data.get('fade_in', {})
            fade_out = data.get('fade_out', {})
            volume_levels_by_keyframes = data.get('volume_levels_by_keyframes', {})
            volume_levels_by_name = data.get('volume_levels_by_name', {})
    except OSError:
        pass


def register():
    bpy.utils.register_class(CountKeyframesOperator)
    bpy.utils.register_class(CrossfadeOperator)
    bpy.utils.register_class(CrossfadePanel)
    bpy.utils.register_class(SetCrossfadeFramesOperator)
    bpy.types.Scene.crossfade_frames = bpy.props.IntProperty(
        name='crossfade_frames',
        default=30,
        min=0,
    )


def set_fade_in(left):
    if left.name not in fade_in:
        return None
    volume_levels[left][left.frame_final_start] = 0
    for name, volume in volume_levels_by_name.items():
        if left.name.startswith(name):
            volume_levels[left][left.frame_final_start + fade_in[left.name]] = volume
            break
    else:
        volume_levels[left][left.frame_final_start + fade_in[left.name]] = 1


def set_fade_out(left):
    if left.name not in fade_out:
        return None
    for name, volume in volume_levels_by_name.items():
        if left.name.startswith(name):
            volume_levels[left][left.frame_final_end - fade_out[left.name]] = volume
            break
    else:
        volume_levels[left][left.frame_final_end - fade_out[left.name]] = 1
    volume_levels[left][left.frame_final_end] = 0


def set_volume_levels():
    for strip, config in volume_levels.items():
        for keyframe, volume in config.items():
            strip.volume = volume
            strip.keyframe_insert('volume', frame=keyframe)


def set_volume_levels_by_keyframes(left):
    for name, keyframes in volume_levels_by_keyframes.items():
        if left.name.startswith(name):
            for config in keyframes:
                volume_levels[left][config[0]] = config[1]
            break


def set_volume_levels_by_name(left):
    for name, volume in volume_levels_by_name.items():
        if left.name.startswith(name):
            if left.frame_final_start not in volume_levels[left]:
                volume_levels[left][left.frame_final_start] = volume
            if left.frame_final_end not in volume_levels[left]:
                volume_levels[left][left.frame_final_end] = volume
            break


def unregister():
    bpy.utils.unregister_class(CountKeyframesOperator)
    bpy.utils.unregister_class(CrossfadeOperator)
    bpy.utils.unregister_class(CrossfadePanel)
    bpy.utils.unregister_class(SetCrossfadeFramesOperator)


if __name__ == '__main__':
    register()
