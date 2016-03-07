from xml.dom import minidom
import os
import psutil
import time
import re

eztv_rss = open('ezrss.xml')
eztv_doc = minidom.parse(eztv_rss)
show_list = eztv_doc.getElementsByTagName('item')
pythons_psutil = []
my_shows = ['Stephen Colbert', 'Conan', 'Jimmy Fallon', 'Yukon Gold']
magnets = []

# Loop needs to be changed so that every 'x' amount of time the app check
# if the process is active and only then compute, otherwise it needs to sleep
# for 'x' seconds.
for p in psutil.process_iter():
    if p.name() == 'openvpn-gui.exe':
        for show in show_list:
            title = show.getElementsByTagName('title')[0].childNodes[0].nodeValue
            try:
                # This is a temp regex solution that looks for patterns like s09e01 which
                # is the standard when namin a tv show file
                match = re.search(r's[0-9]{2}e[0-9]{2}', title, re.IGNORECASE).group(0)
                # Once the regex catches the interesting part, the title will be filtered, every word of it capitalized
                # and whitespace trimmed
                filtered_title = title.split(match)[0].title().strip()
            except AttributeError:
                filtered_title = title

            if filtered_title in my_shows:
                print filtered_title
                # magnet_link = s.getElementsByTagName('torrent:magnetURI')[0].childNodes[0].nodeValue
                # os.startfile(magnet_link)
