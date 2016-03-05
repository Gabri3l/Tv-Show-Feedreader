from xml.dom import minidom
import os
import psutil
import time

eztv_rss = open('ezrss.xml')
eztv_doc = minidom.parse(eztv_rss)
show_list = eztv_doc.getElementsByTagName('item')
pythons_psutil = []
my_shows = ['Stephen Colbert', 'Conan', 'Jimmy Fallon']
magnets = []

# Loop needs to be changed so that every 'x' amount of time the app check
# if the process is active and only then compute, otherwise it needs to sleep
# for 'x' seconds.
for p in psutil.process_iter():
    if p.name() == 'openvpn-gui.exe':
        for show in show_list:
            title = show.getElementsByTagName('title')[0].childNodes[0].nodeValue
            # title needs to be filtered using regex to filter out only the title with nothing else
            # this way only the shows that are in the user favourites will be then processed
            if title in my_shows:
                # magnet_link = s.getElementsByTagName('torrent:magnetURI')[0].childNodes[0].nodeValue
                # os.startfile(magnet_link)
