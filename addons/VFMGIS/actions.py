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
        from javax.swing import JOptionPane
        from org.gvsig.andami import PluginServices
        JOptionPane.showMessageDialog(PluginServices.getMainFrame(),
            u"VFMGIS 0.2 · Lõi và giao diện gvSIG 2.6.0 build 3335\n"
            u"Bản địa hóa tiếng Việt · GPL-3.0-or-later\n"
            u"Bản dịch đang được rà soát; xem báo cáo độ phủ trong gói phát hành.\n"
            u"Bản quyền lõi: gvSIG Association và các tác giả gốc.", u"Giới thiệu VFMGIS",
            JOptionPane.INFORMATION_MESSAGE)


def selfRegister():
    global _registered
    if _registered:
        return
    manager = PluginsLocator.getActionInfoManager()
    action = manager.createAction(VFMGISExtension(), 'vfmgis-open', u'Giới thiệu VFMGIS',
                                  'vfmgis-open', None, None, 900000000,
                                  u'GIS tiếng Việt trên lõi gvSIG gốc')
    action = manager.registerAction(action)
    ApplicationLocator.getManager().addMenu(action, u'VFMGIS/Giới thiệu VFMGIS')
    _registered = True
