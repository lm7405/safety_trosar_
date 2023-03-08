from safetyTrosar.mainWindow import show_main_window
from safetyTrosar.tool import singletonProgram


def run(argv):
    if singletonProgram.is_port_enable():
        # singletonProgram.start_listen()
        show_main_window(argv)
    else:
        message = argv[1]
        singletonProgram.send(message)
