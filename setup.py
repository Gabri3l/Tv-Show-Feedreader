from distutils.core import setup
import py2exe

setup(
    name='Tv-Show-Feedreader',
    version='1.0',
    packages=[''],
    url='http://gabri3l.github.io/Tv-Show-Feedreader/',
    license='MIT',
    author='Gabriele Cimato',
    author_email='gabriele.cimato@gmail.com',
    description='Simple automated tv show feed reader',
    windows=[
        {
            "script": "tv_show_feedreader.py",
            "icon_resources": [(0, "ticket.ico")]
        }
    ]
    # options={'py2exe': {'bundle_files': 1}},
)

# includes = []
# excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
#             'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
#             'Tkconstants', 'Tkinter']
# packages = []
# dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
#                 'tk84.dll']
#
# setup(
#     options = {"py2exe": {"compressed": 2,
#                           "optimize": 2,
#                           "includes": includes,
#                           "excludes": excludes,
#                           "packages": packages,
#                           "dll_excludes": dll_excludes,
#                           "bundle_files": 3,
#                           "dist_dir": "dist",
#                           "xref": False,
#                           "skip_archive": False,
#                           "ascii": False,
#                           "custom_boot_script": '',
#                          }
#               },
#     windows=['tv_show_feedreader.py']
# )