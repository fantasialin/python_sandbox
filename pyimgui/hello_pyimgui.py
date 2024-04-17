# -*- coding: utf-8 -*-
import os
import sys
import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

path_to_font = "Roboto-Regular.ttf"

opened_state = True


def frame_commands():
    io = imgui.get_io()
    if io.key_ctrl and io.keys_down[glfw.KEY_Q]:
        sys.exit(0)

    if imgui.begin_main_menu_bar():
        if imgui.begin_menu('File'):
            clicked, selected = imgui.menu_item("Quit", "Ctrl+Q")
            if clicked:
                sys.exit(0)
            imgui.end_menu()
        imgui.end_main_menu_bar()
    
    imgui.set_next_window_size(300, 200)
    imgui.set_next_window_position(10, 50)

    #use with without need to end() the begin..()
    with imgui.begin("A Window!"):
        if imgui.button("select"):
            imgui.open_popup("select-popup")
        try:
            with imgui.begin_popup("select-popup") as popup:
                if popup.opened:
                    imgui.text("Select one")
        except Exception:
            print(f'caught ...')

    imgui.set_next_window_size(300, 200)
    imgui.set_next_window_position(10, 250)
    imgui.begin("B Window!")
    imgui.text("Hi ....")
    imgui.end() #you need end(), otherwise imgui.core will terminate execution.




class root_window():
    # constructor
    def __init__(self, width, height, **kwargs):
        print(f'root_window init')
        self.window = None
        self.impl = None
        self.font_new = None
        self.inited = False
        self.width = width
        self.height = height
        self.name = kwargs.get('app_name', 'ImGui/GLFW3 app')
        self.font_name = kwargs.get('font_name', "Roboto-Regular.ttf")

        imgui.create_context()

        if glfw.init():
            if self.impl_glfw_init():
                self.inited = True
                self.impl = GlfwRenderer(self.window)

                #set font
                io = imgui.get_io()
                font_scaling_factor = 2
                font_size_in_pixels = 30

                self.font_new = io.fonts.add_font_from_file_ttf(
                    self.font_name, font_size_in_pixels * font_scaling_factor)
                io.font_global_scale /= font_scaling_factor
                self.impl.refresh_font_texture()



    # destructor
    def __del__(self):
        print(f'root_window destructor')
        if self.impl != None:
            self.impl.shutdown()
        glfw.terminate()

    def get_init_status(self):
        return self.inited
    
    def main_loop(self):
        while not glfw.window_should_close(self.window):
            self.render_frame()

    def render_frame(self):
        # pre-process mouse input and keyboard and new a frame.
        glfw.poll_events()
        self.impl.process_inputs()
        imgui.new_frame()

        # clear the window buffer
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)


        if self.font_new is not None:
            imgui.push_font(self.font_new)
        # GUI command handling..
        frame_commands()
        if self.font_new is not None:
            imgui.pop_font()

        # rendering
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        glfw.swap_buffers(self.window)



    def impl_glfw_init(self):
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        self.window = glfw.create_window(int(self.width), int(self.height), self.name, None, None)
        glfw.make_context_current(self.window)
        if not self.window:
            return False
        return True

def main():
    
    window = root_window(800,600)
    if window.get_init_status():
        window.main_loop()
    else:
        #failed init destroy window
        del window

if __name__ == "__main__":
    main()