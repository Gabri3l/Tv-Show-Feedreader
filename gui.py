import wx
import psutil
import urllib2
import re
import xml.etree.ElementTree as ET
import os
from mail_ico import getIcon


# TODO: If running continuously it should check the feed every 24 hours
# TODO: Add video quality preference (720 or normal)
# TODO: Save VPN toggle preference in config
class MailIcon(wx.TaskBarIcon):
    TB_MENU_RESTORE = wx.NewId()
    TB_MENU_CLOSE = wx.NewId()
    TB_MENU_START = wx.NewId()
    TB_MENU_STOP = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        self.tbIcon = getIcon()

        self.SetIcon(self.tbIcon, "Tv Show Feed Reader")

        # Bind some events
        self.Bind(wx.EVT_MENU, self.on_restore, id=self.TB_MENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.frame.gui.on_start, id=self.TB_MENU_START)
        self.Bind(wx.EVT_MENU, self.frame.gui.on_stop, id=self.TB_MENU_STOP)
        self.Bind(wx.EVT_MENU, self.frame.gui.on_quit, id=self.TB_MENU_CLOSE)

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_taskbar_leftclick)

    def create_popup_menu(self, event=None):
        menu = wx.Menu()
        menu.Append(self.TB_MENU_RESTORE, "Open Program")
        menu.Append(self.TB_MENU_START, "Start Program")
        menu.Append(self.TB_MENU_STOP, "Stop Program")
        menu.AppendSeparator()
        menu.Append(self.TB_MENU_CLOSE,   "Exit Program")
        return menu

    def on_taskbar_leftclick(self, event):
        menu = self.create_popup_menu()
        self.PopupMenu(menu)
        menu.Destroy()

    def on_restore(self, event):
        self.frame.Iconize(False)
        self.frame.Raise()


class AppGui:

    ID_CLEAR_CACHE = wx.NewId()

    def __init__(self, frame):
        self.frame = frame
        panel = wx.Panel(frame, wx.ID_ANY)

        # Menu
        frame.CreateStatusBar()
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        save_config_item = wx.MenuItem(file_menu, wx.ID_SAVE, "Save config",
                                       "This will save the current configuration.")
        # load_config_item = wx.MenuItem(file_menu, wx.ID_OPEN, "Load config",
        #                                "This will load a configuration from file.")
        clear_cache_item = wx.MenuItem(file_menu, self.ID_CLEAR_CACHE, "Clear cache",
                                       "This will clear the list of previously downloaded shows.")
        close_app_item = wx.MenuItem(file_menu, wx.ID_EXIT, "Close", "Close the application.")
        file_menu.AppendItem(save_config_item)
        # file_menu.AppendItem(load_config_item)
        file_menu.AppendItem(clear_cache_item)
        file_menu.AppendSeparator()
        file_menu.AppendItem(close_app_item)
        menu_bar.Append(file_menu, "File")

        # File menu bindings
        frame.Bind(wx.EVT_MENU, self.save_config, save_config_item)
        frame.Bind(wx.EVT_MENU, self.clear_observed_list, clear_cache_item)
        frame.Bind(wx.EVT_MENU, self.on_quit, close_app_item)
        frame.Bind(wx.EVT_CLOSE, self.on_quit)
        frame.SetMenuBar(menu_bar)

        # Vpn static box
        wx.StaticBox(panel, 6, 'VPN Status', (10, 10), (570, 100))

        wx.StaticText(panel, 4, 'Are you going to use a VPN ?', (25, 35))
        self.vpn_yes = wx.RadioButton(panel, 7, 'Yes', pos=(420, 35), style=wx.RB_GROUP)
        self.vpn_no = wx.RadioButton(panel, 7, 'No', pos=(510, 35))

        self.vpn_text_area = wx.TextCtrl(panel, 2, pos=(20, 70), size=(350, 25), style=wx.TE_READONLY)
        self.open_file_button = wx.Button(panel, wx.ID_ANY, 'Select VPN', (390, 70))
        self.clear_file_button = wx.Button(panel, wx.ID_ANY, 'Clear', (480, 70))

        # Tv shows static box
        wx.StaticBox(panel, 6, 'Tv Shows List', (10, 110), (570, 115))

        self.tv_show_text_area = wx.TextCtrl(panel, 2, pos=(20, 135), size=(350, 75),
                                             style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.add_show_button = wx.Button(panel, wx.ID_ANY, 'Add Show', (390, 135))
        self.del_show_button = wx.Button(panel, wx.ID_ANY, 'Del Show', (480, 135))
        self.del_all_show_button = wx.Button(panel, wx.ID_ANY, 'Del All', (480, 165))

        # App start and stop
        self.start_button = wx.Button(panel, wx.ID_ANY, 'Start', (390, 240))
        self.stop_button = wx.Button(panel, wx.ID_ANY, 'Stop', (480, 240))

        # Buttons bindings
        self.vpn_yes.Bind(wx.EVT_RADIOBUTTON, self.toggle_vpn)
        self.vpn_no.Bind(wx.EVT_RADIOBUTTON, self.toggle_vpn)
        self.open_file_button.Bind(wx.EVT_BUTTON, self.on_find_vpn_path)
        self.clear_file_button.Bind(wx.EVT_BUTTON, self.on_clear_vpn_path)

        self.add_show_button.Bind(wx.EVT_BUTTON, self.on_add_show)
        self.del_show_button.Bind(wx.EVT_BUTTON, self.on_del_show)
        self.del_all_show_button.Bind(wx.EVT_BUTTON, self.on_del_all_shows)

        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop)

        # Execution
        self.load_config(None)
        self.load_observed_list()
        self.frame.start_up = False

    #########################################################
    #                                                       #
    #                VPN RELATED METHODS                    #
    #                                                       #
    #########################################################
    def on_find_vpn_path(self, event):
        open_file_dialog = wx.FileDialog(self.frame, "Open", "", "",
                                         "Executables (*.exe)|*.exe",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if open_file_dialog.ShowModal() == wx.ID_OK:
            vpn_path = open_file_dialog.GetPath()
            self.vpn_text_area.SetValue(vpn_path)
            self.frame.config_changed = True
            self.frame.vpn = vpn_path[vpn_path.rfind('\\') + 1:]

    def on_clear_vpn_path(self, event):
        self.vpn_text_area.SetValue('')
        self.frame.vpn = ''

    def check_vpn(self, event):
        vpn_app = self.vpn_text_area.GetValue()  # This value needs to be filtered with a regex
        is_vpn_active = False
        if vpn_app == '' or vpn_app == 'Please provide a valid application path':
            self.vpn_text_area.SetValue('Please provide a valid application path.')
        else:
            for p in psutil.process_iter():
                if p.name() == self.frame.vpn:
                    is_vpn_active = True

            if not is_vpn_active:
                wx.MessageBox('Your VPN is not running. Make sure to protect your connection.',
                              'No VPN active', wx.OK | wx.ICON_ERROR)
        return is_vpn_active

    def toggle_vpn(self, event):
        if self.vpn_no.GetValue():
            self.open_file_button.Disable()
            self.frame.use_vpn = False
        else:
            self.open_file_button.Enable()
            self.frame.use_vpn = True

    #########################################################
    #                                                       #
    #           APP LIFECYCLE RELATED METHODS               #
    #                                                       #
    #########################################################
    def on_start(self, event):
        if self.frame.use_vpn:
            is_vpn_active = self.check_vpn(event)
        else:
            is_vpn_active = True

        if is_vpn_active and len(self.frame.favourite_shows) > 0:
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
                        full_title = filtered_title + ' ' + match
                    except AttributeError:
                        filtered_title = title
                    # Checks that the show is in the user favourite list and that the title has not been previously
                    # downloaded, such info is stored in the observed_shows array
                    if (filtered_title in self.frame.favourite_shows) and (full_title not in self.frame.observed_shows):
                        # magnet_link = child.find('{http://xmlns.ezrss.it/0.1/}magnetURI').text
                        # os.startfile(magnet_link)
                        self.update_observed_list(full_title)

        elif is_vpn_active:
            wx.MessageBox('There are no shows in your list. Please make sure to add at least one.',
                          'No shows found.', wx.OK | wx.ICON_INFORMATION)

    def on_stop(self, event):
        pass

    def on_quit(self, event):
        if self.frame.config_changed and (self.frame.vpn != '' or len(self.frame.favourite_shows) > 0):
            save_before_exit = wx.MessageDialog(None, 'Do you want to save your changes?',
                                                'Save current configuration', wx.YES_NO | wx.ICON_INFORMATION)
            if save_before_exit.ShowModal() == wx.ID_YES:
                self.save_config(event)
        self.frame.tbIcon.RemoveIcon()
        self.frame.tbIcon.Destroy()
        self.frame.Destroy()

    #########################################################
    #                                                       #
    #                CONFIG RELATED METHODS                 #
    #                                                       #
    #########################################################
    def save_config(self, event):
        with open('config.dat', 'w') as f:
            f.write(self.vpn_text_area.GetValue() + '\n')
            if len(self.frame.favourite_shows) > 0:
                f.write(self.tv_show_text_area.GetValue())
            self.frame.config_changed = False

    def load_config(self, event):
        try:
            with open('config.dat', 'r') as f:
                saved_vpn_path = f.readline()
                saved_shows = f.readline()

                if saved_vpn_path:
                    self.vpn_text_area.SetValue(saved_vpn_path[:-1])
                    self.frame.vpn = saved_vpn_path[saved_vpn_path.rfind('\\') + 1:-1]
                if saved_shows != '':
                    self.tv_show_text_area.SetValue(saved_shows)
                    self.frame.favourite_shows = saved_shows.split(', ')
        except IOError:
            if not self.frame.start_up:
                wx.MessageBox('No config file could be found.',
                              'Missing config!', wx.OK | wx.ICON_ERROR)

    def update_observed_list(self, tv_show_title):
        with open('observed.dat', 'a') as f:
            f.write(tv_show_title + ';')
        self.frame.observed_shows.append(tv_show_title)

    def load_observed_list(self):
        try:
            with open('observed.dat', 'r') as f:
                self.frame.observed_shows = f.readline().split(';')
        except IOError:
            pass

    def clear_observed_list(self, event):
        clear_cache_box = wx.MessageDialog(None, 'This will empty the list of previously downloaded shows, do you '
                                                 'really want to proceed ?',
                                           'Clear downloaded shows cache', wx.YES_NO | wx.ICON_INFORMATION)
        if clear_cache_box.ShowModal() == wx.ID_YES:
            self.frame.observed_shows = []
            # Empties the file from its content
            open('observed.dat', 'w').close()

    #########################################################
    #                                                       #
    #                TV SHOW RELATED METHODS                #
    #                                                       #
    #########################################################
    def on_add_show(self, event):
        show_box = wx.TextEntryDialog(None, 'What show would you like to add?', 'Add Show', 'Show name')
        if show_box.ShowModal() == wx.ID_OK:
            new_show = show_box.GetValue().title().strip()
            if self.tv_show_text_area.GetValue() == '':
                self.tv_show_text_area.SetValue(new_show)
                self.frame.favourite_shows.append(new_show)
                self.frame.config_changed = True
            else:
                current_shows = self.tv_show_text_area.GetValue().split(', ')
                if new_show in current_shows:
                    wx.MessageBox('The show provided is already in the list.',
                                  'Duplicate found!', wx.OK | wx.ICON_EXCLAMATION)
                else:
                    self.tv_show_text_area.AppendText(', ' + new_show)
                    self.frame.favourite_shows.append(new_show)
                    self.frame.config_changed = True
        show_box.SetValue('Show name')

    def on_del_show(self, event):
        del_show_box = wx.TextEntryDialog(None, 'Which show would you like to remove?', 'Del Show', 'Show name')
        if del_show_box.ShowModal() == wx.ID_OK:
            to_del_show = del_show_box.GetValue().title().strip()
            current_shows = self.tv_show_text_area.GetValue().split(', ')
            if to_del_show not in current_shows:
                wx.MessageBox('The show specified is not in the list.',
                              'Can\'t remove show', wx.OK | wx.ICON_INFORMATION)
            else:
                current_shows.remove(to_del_show)
                self.frame.favourite_shows.remove(to_del_show)
                self.tv_show_text_area.SetValue('')
                for index, show in enumerate(current_shows):
                    if index < len(current_shows) - 1:
                        self.tv_show_text_area.AppendText(show + ', ')
                    else:
                        self.tv_show_text_area.AppendText(show)
        del_show_box.SetValue('Show name')

    def on_del_all_shows(self, event):
        del_all_shows_box = wx.MessageDialog(None, 'Do you really want to remove all shows from your list?',
                                             'Delete all shows', wx.YES_NO | wx.ICON_INFORMATION)
        if del_all_shows_box.ShowModal() == wx.ID_YES:
            self.tv_show_text_area.SetValue('')
            self.frame.favourite_shows = []


class WindowClass(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(WindowClass, self).__init__(*args, **kwargs)

        self.vpn = ''
        self.quality = ''
        self.use_vpn = True
        self.config_changed = False
        self.favourite_shows = []
        self.observed_shows = []
        self.start_up = True

        self.gui = AppGui(self)
        self.tbIcon = MailIcon(self)

        self.Center()
        self.Show()


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
    WindowClass(None, title='Tv Show Feed Reader', size=(595, 350), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    app.MainLoop()
