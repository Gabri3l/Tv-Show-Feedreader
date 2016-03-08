import wx


class WindowClass(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(WindowClass, self).__init__(*args, **kwargs)
        self.add_gui()
        self.Center()
        self.Show()

    def add_gui(self):

        def on_button(event):
            open_file_dialog = wx.FileDialog(self, "Open", "", "",
                                             "Executables (*.exe)|*.exe",
                                             wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            open_file_dialog.ShowModal()
            text_area.SetValue(open_file_dialog.GetPath())

        panel = wx.Panel(self, wx.ID_ANY)
        button = wx.Button(panel, wx.ID_ANY, 'Select VPN', (250, 10))
        text_area = wx.TextCtrl(panel, pos=(10, 10), size=(230, 25))
        # dlg = wx.TextEntryDialog(panel, 'Enter text', 'some text', pos=(10,10))
        button.Bind(wx.EVT_BUTTON, on_button)

if __name__ == '__main__':
    app = wx.App()
    WindowClass(None, title='Tv Show AutoDownload', size=(640, 480))
    app.MainLoop()
