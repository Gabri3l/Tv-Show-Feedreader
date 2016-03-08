import wx
import psutil


class WindowClass(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(WindowClass, self).__init__(*args, **kwargs)
        self.add_gui()
        self.Center()
        self.Show()

    def add_gui(self):

        def check_vpn():
            vpn_app = vpn_text_area.GetValue()  # This value needs to be filtered with a regex
            is_vpn_active = False
            if vpn_app == '':
                vpn_text_area.SetValue('Please provide a valid application path')
                print 'no vpn name specified'
            elif vpn_app == 'Please provide a valid application path':
                print 'no vpn name specified'
            else:
                for p in psutil.process_iter():
                    if p.name() == 'openvpn-gui.exe':
                        is_vpn_active = True

                if is_vpn_active:
                    print "vpn is active"
                else:
                    print 'vpn is not active'
            return is_vpn_active

        def on_button(event):
            open_file_dialog = wx.FileDialog(self, "Open", "", "",
                                             "Executables (*.exe)|*.exe",
                                             wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            open_file_dialog.ShowModal()
            vpn_text_area.SetValue(open_file_dialog.GetPath())

        def on_start(event):
            check_vpn()

        panel = wx.Panel(self, wx.ID_ANY)

        # buttons
        open_file_button = wx.Button(panel, wx.ID_ANY, 'Select VPN', (530, 10))
        start_button = wx.Button(panel, wx.ID_ANY, 'Start', (250, 390))

        # buttons bindings
        open_file_button.Bind(wx.EVT_BUTTON, on_button)
        start_button.Bind(wx.EVT_BUTTON, on_start)

        vpn_text_area = wx.TextCtrl(panel, 2, pos=(10, 10), size=(510, 25))
        vpn_text_area.Disable()


if __name__ == '__main__':
    app = wx.App()
    WindowClass(None, title='Tv Show AutoDownload', size=(640, 480))
    app.MainLoop()
