# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
# Registration pattern adapted from gvSIGAssociation CoordinateCapture/actions.py
# Copyright (C) 2007-2018 gvSIG Association; additions (C) 2026 Long Ngo.
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
_registered = False


class VFMGISExtension(ScriptingExtension):
    def canQueryByAction(self):
        return True

    def isEnabled(self, action):
        return True

    def isVisible(self, action):
        return True

    def execute(self, actionCommand, *args):
        from addons.VFMGIS.ui import main
        main()


def selfRegister():
    global _registered
    if _registered:
        return
    manager = PluginsLocator.getActionInfoManager()
    action = manager.createAction(VFMGISExtension(), 'vfmgis-open', u'Mở VFMGIS',
                                  'vfmgis-open', None, None, 900000000,
                                  u'Không gian GIS cơ bản bằng tiếng Việt')
    action = manager.registerAction(action)
    ApplicationLocator.getManager().addMenu(action, u'VFMGIS/Mở VFMGIS')
    _registered = True
