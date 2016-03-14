import wx
import psutil
import urllib2
import re
import xml.etree.ElementTree as ET
import os


# TODO: Allow app to run in background or tray icon
# TODO: If running continuously it should check the feed every 24 hours
# TODO: Provide list of observed items during app running time
# TODO: Change Shows text view to scrollable text view
# TODO: Ask to save changes on exit
class WindowClass(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(WindowClass, self).__init__(*args, **kwargs)
        self.vpn = ''
        self.use_vpn = True
        self.favourite_shows = []
        self.start_up = True
        self.add_gui()
        self.Center()
        self.Show()

    def add_gui(self):

        def check_vpn():
            vpn_app = vpn_text_area.GetValue()  # This value needs to be filtered with a regex
            is_vpn_active = False
            if vpn_app == '' or vpn_app == 'Please provide a valid application path':
                vpn_text_area.SetValue('Please provide a valid application path.')
            else:
                for p in psutil.process_iter():
                    if p.name() == self.vpn:
                        is_vpn_active = True

                if not is_vpn_active:
                    wx.MessageBox('Your VPN is not running. Make sure to protect your connection.',
                                  'No VPN active', wx.OK | wx.ICON_ERROR)
            return is_vpn_active

        def on_button(event):
            open_file_dialog = wx.FileDialog(self, "Open", "", "",
                                             "Executables (*.exe)|*.exe",
                                             wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if open_file_dialog.ShowModal() == wx.ID_OK:
                vpn_path = open_file_dialog.GetPath()
                vpn_text_area.SetValue(vpn_path)
                self.vpn = vpn_path[vpn_path.rfind('\\') + 1:]

        def on_clear(event):
            vpn_text_area.SetValue('')

        def on_add_show(event):
            if show_box.ShowModal() == wx.ID_OK:
                new_show = show_box.GetValue().title().strip()
                if tv_show_text_area.GetValue() == '':
                    tv_show_text_area.SetValue(new_show)
                    self.favourite_shows.append(new_show)
                else:
                    current_shows = tv_show_text_area.GetValue().split(', ')
                    if new_show in current_shows:
                        wx.MessageBox('The show provided is already in the list.',
                                      'Duplicate found!', wx.OK | wx.ICON_EXCLAMATION)
                    else:
                        tv_show_text_area.AppendText(', ' + new_show)
                        self.favourite_shows.append(new_show)
            show_box.SetValue('Show name')

        def on_del_show(event):
            if del_show_box.ShowModal() == wx.ID_OK:
                to_del_show = del_show_box.GetValue().title().strip()
                current_shows = tv_show_text_area.GetValue().split(', ')
                if to_del_show not in current_shows:
                    wx.MessageBox('The show specified is not in the list.',
                                  'Can\'t remove show', wx.OK | wx.ICON_INFORMATION)
                else:
                    current_shows.remove(to_del_show)
                    self.favourite_shows.remove(to_del_show)
                    tv_show_text_area.SetValue('')
                    for index, show in enumerate(current_shows):
                        if index < len(current_shows) - 1:
                            tv_show_text_area.AppendText(show + ', ')
                        else:
                            tv_show_text_area.AppendText(show)
            del_show_box.SetValue('Show name')

        def on_del_all_shows(event):
            if del_all_shows_box.ShowModal() == wx.ID_YES:
                tv_show_text_area.SetValue('')
                self.favourite_shows = []

        def on_start(event):
            if self.use_vpn:
                is_vpn_active = check_vpn()
            else:
                is_vpn_active = True

            if is_vpn_active and len(self.favourite_shows) > 0:
                show_xml = request_xml('https://eztv.ag/ezrss.xml')
                if show_xml != '':
                    show_list_root = ET.fromstring(show_xml).find('channel')

                    for child in show_list_root.findall('item'):
                        title = child.find('title').text
                        try:
                            # This is a temp regex solution that looks for patterns like s09e01 which
                            # is the standard when naming a tv show file
                            match = re.search(r's[0-9]{2}e[0-9]{2}', title, re.IGNORECASE).group(0)
                            filtered_title = title.split(match)[0].title().strip()
                        except AttributeError:
                            filtered_title = title
                        if filtered_title in self.favourite_shows:
                            magnet_link = child.find('{http://xmlns.ezrss.it/0.1/}magnetURI').text
                            os.startfile(magnet_link)
            elif is_vpn_active:
                wx.MessageBox('There are no shows in your list. Please make sure to add at least one.',
                              'No shows found.', wx.OK | wx.ICON_INFORMATION)

        def toggle_vpn(event):
            if vpn_no.GetValue():
                open_file_button.Disable()
                self.use_vpn = False
            else:
                open_file_button.Enable()
                self.use_vpn = True

        def save_config(event):
            print 'saving'
            f = open('config.txt', 'w')
            f.write(vpn_text_area.GetValue() + '\n')
            if len(self.favourite_shows) > 0:
                f.write(tv_show_text_area.GetValue() + '\n')
            f.close()

        def load_config(event):
            try:
                f = open('config.txt', 'r')
                saved_vpn_path = f.readline()
                saved_shows = f.readline()

                if saved_vpn_path:
                    vpn_text_area.SetValue(saved_vpn_path)
                    self.vpn = saved_vpn_path[saved_vpn_path.rfind('\\') + 1:-1]
                if saved_shows != '':
                    tv_show_text_area.SetValue(saved_shows[:-1])
                    self.favourite_shows = saved_shows[:-1].split(', ')
                    print self.favourite_shows
                f.close()
            except IOError:
                if not self.start_up:
                    wx.MessageBox('No config file could be found.',
                                  'Missing config!', wx.OK | wx.ICON_ERROR)

        panel = wx.Panel(self, wx.ID_ANY)

        # menu
        self.CreateStatusBar()
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.NewId(), "Save config", "This will save the current configuration.")
        file_menu.Bind(wx.EVT_MENU, save_config)
        file_menu.Append(wx.NewId(), "Load config", "This will load a configuration from file")
        menu_bar.Append(file_menu, "File")
        self.SetMenuBar(menu_bar)

        # vpn static box
        wx.StaticBox(panel, 6, 'VPN Status', (10, 10), (580, 100))

        wx.StaticText(panel, 4, 'Are you going to use a VPN ?', (25, 35))
        vpn_yes = wx.RadioButton(panel, 7, 'Yes', pos=(420, 35), style=wx.RB_GROUP)
        vpn_no = wx.RadioButton(panel, 7, 'No', pos=(510, 35))

        vpn_text_area = wx.TextCtrl(panel, 2, pos=(20, 70), size=(350, 25), style=wx.TE_READONLY)
        open_file_button = wx.Button(panel, wx.ID_ANY, 'Select VPN', (390, 70))
        clear_file_button = wx.Button(panel, wx.ID_ANY, 'Clear', (480, 70))

        # tv-shows static box
        wx.StaticBox(panel, 6, 'Tv Shows List', (10, 110), (580, 120))

        tv_show_text_area = wx.TextCtrl(panel, 2, pos=(20, 135), size=(350, 75), style=wx.TE_READONLY | wx.TE_MULTILINE)
        add_show_button = wx.Button(panel, wx.ID_ANY, 'Add Show', (390, 135))
        del_show_button = wx.Button(panel, wx.ID_ANY, 'Del Show', (480, 135))
        del_all_show_button = wx.Button(panel, wx.ID_ANY, 'Del All', (480, 165))

        # App start and stop
        start_button = wx.Button(panel, wx.ID_ANY, 'Start', (250, 390))
        stop_button = wx.Button(panel, wx.ID_ANY, 'Stop', (340, 390))

        # buttons bindings
        vpn_yes.Bind(wx.EVT_RADIOBUTTON, toggle_vpn)
        vpn_no.Bind(wx.EVT_RADIOBUTTON, toggle_vpn)
        open_file_button.Bind(wx.EVT_BUTTON, on_button)
        clear_file_button.Bind(wx.EVT_BUTTON, on_clear)

        add_show_button.Bind(wx.EVT_BUTTON, on_add_show)
        del_show_button.Bind(wx.EVT_BUTTON, on_del_show)
        del_all_show_button.Bind(wx.EVT_BUTTON, on_del_all_shows)

        start_button.Bind(wx.EVT_BUTTON, on_start)

        # modal
        show_box = wx.TextEntryDialog(None, 'What show would you like to add?', 'Add Show', 'Show name')
        del_show_box = wx.TextEntryDialog(None, 'Which show would you like to remove?', 'Del Show', 'Show name')
        del_all_shows_box = wx.MessageDialog(None, 'Do you really want to remove all shows from your list?',
                                             'Delete all shows', wx.YES_NO | wx.ICON_INFORMATION)

        load_config(None)
        self.start_up = False


def request_xml(site):
    # Only user agent is actually needed to fulfill the request
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(site, headers=hdr)
    try:
        response = urllib2.urlopen(req)
        xml = response.read()
        response.close()
        return xml
    except urllib2.URLError:
        wx.MessageBox('The feed does not exist or is temporary down.',
                      'Can\'t access feed', wx.OK | wx.ICON_ERROR)
        return ''

if __name__ == '__main__':
    app = wx.App()
    WindowClass(None, title='Tv Show Feed Reader', size=(640, 500))
    app.MainLoop()
