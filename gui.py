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

        def on_add_show(event):
            if show_box.ShowModal() == wx.ID_OK:
                new_show = show_box.GetValue()
                if tv_show_text_area.GetValue() == '':
                    tv_show_text_area.SetValue(new_show.title().strip())
                else:
                    current_shows = tv_show_text_area.GetValue().split(', ')
                    if new_show in current_shows:
                        print 'show exists already'
                    else:
                        tv_show_text_area.AppendText(', ' + new_show.title().strip())
            show_box.SetValue('Show name')

        def on_del_show(event):
            if del_show_box.ShowModal() == wx.ID_OK:
                to_del_show = del_show_box.GetValue().title().strip()
                current_shows = tv_show_text_area.GetValue().split(', ')
                if to_del_show not in current_shows:
                    print to_del_show + ' show not in list'
                else:
                    current_shows.remove(to_del_show)
                    tv_show_text_area.SetValue('')
                    for index, show in enumerate(current_shows):
                        if index < len(current_shows) - 1:
                            tv_show_text_area.AppendText(show + ', ')
                        else:
                            tv_show_text_area.AppendText(show)
            del_show_box.SetValue('Show name')

        def on_start(event):
            check_vpn()

        panel = wx.Panel(self, wx.ID_ANY)

        # buttons
        open_file_button = wx.Button(panel, wx.ID_ANY, 'Select VPN', (530, 10))
        add_show_button = wx.Button(panel, wx.ID_ANY, 'Add Show', (440, 45))
        del_show_button = wx.Button(panel, wx.ID_ANY, 'Del Show', (530, 45))
        start_button = wx.Button(panel, wx.ID_ANY, 'Start', (250, 390))

        # buttons bindings
        open_file_button.Bind(wx.EVT_BUTTON, on_button)
        add_show_button.Bind(wx.EVT_BUTTON, on_add_show)
        del_show_button.Bind(wx.EVT_BUTTON, on_del_show)
        start_button.Bind(wx.EVT_BUTTON, on_start)

        # text areas
        vpn_text_area = wx.TextCtrl(panel, 2, pos=(10, 10), size=(510, 25))
        vpn_text_area.Disable()
        tv_show_text_area = wx.TextCtrl(panel, 2, pos=(10, 45), size=(420, 25))
        tv_show_text_area.Disable()

        # modal
        show_box = wx.TextEntryDialog(None, 'What show would you like to add?', 'Add Show', 'Show name')
        del_show_box = wx.TextEntryDialog(None, 'Which show would you like to remove?', 'Del Show', 'Show name')

if __name__ == '__main__':
    app = wx.App()
    WindowClass(None, title='Tv Show AutoDownload', size=(640, 480))
    app.MainLoop()
