from xml.dom import minidom
import os

eztv_rss = open('ezrss.xml')
eztv_doc = minidom.parse(eztv_rss)
itemlist = eztv_doc.getElementsByTagName('item')


for s in itemlist:
    magnet_link = s.getElementsByTagName('torrent:magnetURI')[0].childNodes[0].nodeValue
    # os.startfile(magnet_link)
    print(magnet_link)
