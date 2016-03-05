from xml.dom import minidom
import os
import psutil
import time

eztv_rss = open('ezrss.xml')
eztv_doc = minidom.parse(eztv_rss)
itemlist = eztv_doc.getElementsByTagName('item')
pythons_psutil = []

for p in psutil.process_iter():
    if p.name() == 'openvpn-gui.exe':
        for s in itemlist:
            magnet_link = s.getElementsByTagName('torrent:magnetURI')[0].childNodes[0].nodeValue
            # os.startfile(magnet_link)
            print(magnet_link)
    else:
        time.sleep(10)