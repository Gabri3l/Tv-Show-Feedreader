# Tv-Show-Feedreader
The Tv-Show-Feedreader app uses [eztv](https://eztv.ag/) feeds to be notified when your favourite shows come out. It is a very lightweight software that allows you to build your own list of favorite shows to automatically be downloaded as soon as they come out.

The project was born with research purposes to play with python GUIs. Its primary goal was to build a simple utility very easy to use with no particular expectations.

# Documentation
There is no official documentation for this project, it is completely written in Python and runs in Windows 10 (x64). The code includes sufficient commentary to understand the structure and functionalities of the software.

It has not been tested on other OS besides the one mentioned above, if you run this in a different OS please let me know so I can update the data.

# Installation
There is no special installation required, you can just download or fork the project and either run the script on your terminal:

`python tv_show_feedreader.py`

Or just dowload `tv_show_feedreader.zip` and run the executable. It is a standalone portable software so no installation process is necessary.
# Usage & Bugs
The tv show feedreader retrieves the daily eztv feed and parses the JSON file to extract the necessary info about your favorite shows. Since all of this happens *behind the curtains* the final user has no say in it. There are a few important options that can be manually set up through the GUI.

* **VPN Section**: Here you can specify if you are going to use a VPN or not, and allows you to specify exactly the executable for your VPN. Keep in mind that this will only allow the software to check if the VPN app you are using is currently running but it does not check if the connection of the device you are using is currently protected by a VPN. You need to make sure that the VPN is actually properly connected on your own.
![vpn section](https://raw.githubusercontent.com/Gabri3l/Tv-Show-Feedreader/master/images/tv-show-feedreader-1.PNG)
* **TV Show Section**: Here you can list all of the shows you are following or interested in, along with your favorite resolution (480p, 720p or 1080p). Another note here, the software currently only check if the resolution selected is available, if not the download will not start.
![tv show section](https://raw.githubusercontent.com/Gabri3l/Tv-Show-Feedreader/master/images/tv-show-feedreader-2.PNG)

Once the **Start** button is pressed, the software will download and check the xml file every 12 hours. If a specific episode has already been downloaded, it will not start its download again.

About the **downloading** aspect, this application will open the magnet links ![magnet icon](https://raw.githubusercontent.com/Gabri3l/Tv-Show-Feedreader/master/images/magnet.png) using the default software used by your OS. The app is not a torrent client, this app will invoke your torrent client automatically once a new episode is out.

The way the app knows if an episode has been downloaded is by saving in a local file the name of the show and the episode number, as soon as the magnet link has been activated. Naturally this local file can be emptied through the **File** menu.

The current configuration set up by the user can also be saved through the **File** menu and it is automatically loaded once the app is started.

There are no known bugs at the time of this release (1.0), please let me know if you find one.
# Contributing
Feel free to make any pull request to update this software. There are a couple features that can be added along with the support for more tv show feeds and vpn software.

* There is no *fallback* for the video quality check, if the show is not present at the video quality selected by the user then it will not be downloaded. It clearly would be nice to be able to download the lower quality if the selected one is not available
* There is no current feature that allows to guarantee if the connection is running through a VPN, it only checks if the app specified is currently running in the system. I was not able to find a solution that would fit every case but I have found a solution (not yet implemented) for the following VPN software:
	* openvpn-gui.exe 

Such solution will check the log file generated by the software from which we can infer if the vpn is properly running. Unforunately this might not be true for every VPN, please report the VPN software you are using and I might be able to find a way to check if the connection is actually protected.
# License

Feel free to use this code as you wish, edit it, customize it, it is free with an **MIT** license! 

