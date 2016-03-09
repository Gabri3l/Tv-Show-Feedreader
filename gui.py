import wx
import psutil
import urllib2
import re
import xml.etree.ElementTree as ET


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
            # TODO The request has to start only if vpn is active
            show_list_root = ET.fromstring(request_xml('https://eztv.ag/ezrss.xml')).find('channel')

            for child in show_list_root.findall('item'):
                title = child.find('title').text
                try:
                    # This is a temp regex solution that looks for patterns like s09e01 which
                    # is the standard when naming a tv show file
                    match = re.search(r's[0-9]{2}e[0-9]{2}', title, re.IGNORECASE).group(0)
                    filtered_title = title.split(match)[0].title().strip()
                except AttributeError:
                    filtered_title = title

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


def request_xml(site):
    # Only user agent is actually needed to fulfill the request
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(site, headers=hdr)
    response = urllib2.urlopen(req)
    xml = response.read()
    response.close()
    return xml

if __name__ == '__main__':
    app = wx.App()
    WindowClass(None, title='Tv Show AutoDownload', size=(640, 480))
    app.MainLoop()
