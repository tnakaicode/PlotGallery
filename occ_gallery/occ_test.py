from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

for i in range(30):
    display, start_display, add_menu, add_function_to_menu = init_display()
