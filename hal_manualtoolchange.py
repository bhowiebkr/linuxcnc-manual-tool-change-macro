#!/usr/bin/python
import sys, os
import gettext
BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
gettext.install("axis", localedir=os.path.join(BASE, "share", "locale"),
unicode=True)

import emc, hal
import rs274.options
iniFile = emc.ini(os.environ['INI_FILE_NAME'])
emc.nmlfile = os.path.join(os.path.dirname(os.environ['INI_FILE_NAME']),
iniFile.find("EMC", "NML_FILE"))

emcStat = emc.stat();
emcCmd = emc.command()

def do_change(n):
    emcStat.poll()
    curLine = emcStat.current_line
    if n:
        message = _("Insert tool %d and click continue when ready") % n
    else:
        message = _("Remove the tool and click continue when ready")
    app.wm_withdraw()
    app.update()
    if curLine >=0:
        emcCmd.abort()
        h.changed = True    
    app.tk.call("nf_dialog", ".tool_change",
        _("Tool change"), message, "info", 0, _("Continue"))
    if curLine >=0:
        emcCmd.mode(emc.MODE_AUTO)
        emcCmd.auto(emc.AUTO_RUN, curLine + 1)
    else:
        h.changed = True    
    app.update()

h = hal.component("hal_manualtoolchange")
h.newpin("number", hal.HAL_S32, hal.HAL_IN)
h.newpin("change", hal.HAL_BIT, hal.HAL_IN)
h.newpin("changed", hal.HAL_BIT, hal.HAL_OUT)
h.ready()

import Tkinter, nf, rs274.options

app = Tkinter.Tk(className="AxisToolChanger")
app.wm_geometry("-60-60")
app.wm_title(_("AXIS Manual Toolchanger"))
rs274.options.install(app)
nf.start(app); nf.makecommand(app, "_", _)
app.wm_protocol("WM_DELETE_WINDOW", app.wm_withdraw)
lab = Tkinter.Message(app, aspect=500, text = _("\
This window is part of the AXIS manual toolchanger.  It is safe to close
\
or iconify this window, or it will close automatically after a few
seconds."))
lab.pack()

def withdraw():
    app.wm_withdraw()
    app.bind("<Expose>", lambda event: app.wm_withdraw())

app.after(10 * 1000, withdraw)

try:
    while 1:
        change = h.change
        if change and not h.changed:
            do_change(h.number)
        elif not change:
            h.changed = False
        app.after(100)
        app.update()
except KeyboardInterrupt:
    pass