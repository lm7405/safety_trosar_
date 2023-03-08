from . import tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget


class SubTabs:
    def __init__(self, main_window, tab_widget):
        self.home = tab1Widget.ProjectWidget(main_window)
        self.requirements = tab2Widget.TabSubWidget(main_window, tab_widget)
        self.hazop = tab3Widget.TabSubWidget(main_window, tab_widget)
        self.safety_measure = tab4Widget.TabSubWidget(main_window, tab_widget)
        self.hazard_log = tab5Widget.TabSubWidget(main_window, tab_widget)
