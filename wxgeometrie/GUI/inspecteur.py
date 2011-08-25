# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Fenetres                              #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from PyQt4.QtGui import QDialog, QVBoxLayout, QHBoxLayout

from .pythonSTC import PythonSTC



class FenCode(QDialog):
    u"""Permet d'�diter du code Python.

    En particulier, permet d'�diter le code de la feuille actuelle."""
    def __init__(self, parent, titre, contenu, fonction_modif):
        QDialog.__init__(self, parent)
        self.setWindowTitle(titre)
        sizer = QVBoxLayout()
        self.parent = parent
        self.fonction_modif = fonction_modif
        self.texte = PythonSTC(self)
#        self.texte.setMinimumSize(300, 10)
        self.texte.setText(contenu)
        self.texte.Bind(wx.EVT_CHAR, self.EvtChar) #XXX
##        self.texte.SetInsertionPointEnd()
        sizer.addWidget(self.texte)

        boutons = QHBoxLayout()
        self.btn_modif = QPushButton(tb, -1, u"Modifier - F5")
        boutons.addWidget(self.btn_modif)
        self.btn_esc = QPushButton(tb, -1, u"Annuler - ESC")
        boutons.addWidget(self.btn_esc)
        sizer.addLayout(boutons)
        self.setLayout(sizer)

        self.btn_modif.connect(self.executer)
        self.btn_esc.connect(self.close)

        self.setMinimumSize(400, 500)
        self.texte.setFocus()


    def keyPressedEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_F5:
            self.executer()
        else:
            QDialog.keyPressedEvent(self, event)


    def executer(self, event = None):
        # On ex�cute le code (de la feuille par ex.) �ventuellement modifi�
        self.fonction_modif(self.texte.text())
        self.close()
