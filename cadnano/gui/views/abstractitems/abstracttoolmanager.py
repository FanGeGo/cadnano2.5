from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QActionGroup

from cadnano import app

class AbstractToolManager(QObject):
    """Manages interactions between the slice widgets/UI and the model."""
    def __init__(self, tool_group_name, window):
        """
        We store mainWindow because a controller's got to have
        references to both the layer above (UI) and the layer below (model)
        """
        super(AbstractToolManager, self).__init__()
        self.window = window
        self.tool_group_name = tool_group_name
        self._active_tool = None
        self._active_part = None
        self.tool_names = None
        self.ag = QActionGroup(window)
    # end def

    ### SIGNALS ###
    activeToolChangedSignal = pyqtSignal(str)

    def installTools(self):
        # Call installTool on every tool
        tnames = self.tool_names
        if tnames is None:
            raise ValueError("Please define tools_names of AbstractToolManager subclass")
        list(map((lambda tool_name: self.ag.addAction(self.installTool(tool_name))),
                        tnames))
        self.ag.setExclusive(True)
        # Select the preferred Startup tool
        startup_tool_name = app().prefs.getStartupToolName()
        getattr(self, 'choose' + startup_tool_name + 'Tool')()
    # end def

    def installTool(self, tool_name):
        window = self.window
        tgn = self.tool_group_name

        l_tool_name = tool_name.lower()
        action_name = 'action_%s_%s' % (tgn, l_tool_name)
        tool_widget = getattr(window, action_name)
        tool = getattr(self, l_tool_name + '_tool')
        tool.action_name = action_name

        set_active_tool_method_name = 'choose%sTool' % (tool_name)

        def clickHandler(self):
            tool_widget.setChecked(True)
            self.setActiveTool(tool)
            if hasattr(tool, 'widgetClicked'):
                tool.widgetClicked()
        # end def

        setattr(self.__class__, set_active_tool_method_name, clickHandler)
        handler = getattr(self, set_active_tool_method_name)
        tool_widget.triggered.connect(handler)
        return tool_widget
    # end def

    def activeToolGetter(self):
        return self._active_tool
    # end def

    def setActiveTool(self, new_active_tool):
        if new_active_tool == self._active_tool:
            return

        # if self.lastLocation():
        #     new_active_tool.updateLocation(*self.lastLocation())

        if self._active_tool is not None:
            self._active_tool.setActive(False)

        self._active_tool = new_active_tool
        self._active_tool.setActive(True)
        self.activeToolChangedSignal.emit(self._active_tool.action_name)
    # end def
# end class