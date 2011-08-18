#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Calculatrice                 #
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

import wx

from ...GUI.ligne_commande import LigneCommande
from ...GUI import MenuBar, Panel_simple
from ... import param
from ...pylib import warning
from ...pylib.erreurs import message
from .tabsign import tabsign
from .tabval import tabval
from .tabvar import tabvar






class TabLaTeXMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", ["quitter"])
        self.ajouter(u"Affichage", ["onglet"])
        self.ajouter(u"Outils",
                        [u"M�moriser le r�sultat", u"Copie le code LaTeX g�n�r� dans le presse-papier, afin de pouvoir l'utiliser ailleurs.", "Ctrl+M", self.panel.vers_presse_papier],
                        None,
                        [u"options"])
        self.ajouter(u"avance2")
        self.ajouter("?")




class TabLaTeX(Panel_simple):
    __titre__ = u"Tableaux LaTeX" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)

        self.sizer = QVBoxLayout()

        self.entree = LigneCommande(self, longueur = 500, action = self.generer_code)
        self.sizer.addWidget(self.entree)

        self.sizer_type = QHBoxLayout()
        self.type_tableau = QComboBox(self)
        self.type_tableau.addItems([u"Tableau de variations", u"Tableau de signes", u"Tableau de valeurs"])
        self.type_tableau.setCurrentIndex(self._param_.mode)
        self.sizer_type.addWidget(QLabel(u"Type de tableau � g�n�rer :", self))
        self.sizer_type.addWidget(self.type_tableau)

        self.utiliser_cellspace = QCheckBox(self, label = u"Utiliser le paquetage cellspace.")
        self.utiliser_cellspace.setChecked(self._param_.utiliser_cellspace)
        self.utiliser_cellspace.setToolTip(u"Le paquetage cellspace �vite que certains objets (comme les fractions) touchent les bordures du tableaux.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.utiliser_cellspace)

        self.derivee = QCheckBox(self, label = u"D�riv�e.")
        self.derivee.setChecked(self._param_.derivee)
        self.derivee.setToolTip(u"Afficher une ligne indiquant le signe de la d�riv�e.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.derivee)

        self.limites = QCheckBox(self, label = u"Limites.")
        self.limites.setChecked(self._param_.limites)
        self.limites.setToolTip(u"Afficher les limites dans le tableau de variations.")
        self.sizer_type.addSpacing(10)
        self.sizer_type.addWidget(self.limites)

        self.sizer.addLayout(self.sizer_type)

        box = QGroupBox(u"Code LaTeX permettant de de g�n�rer le tableau", self)
        self.bsizer = QVBoxLayout()
        self.bsizer.setLayout(box)

        self.code_tableau = wx.TextCtrl(self, size = (700, 200), style = wx.TE_MULTILINE | wx.TE_RICH)
        self.bsizer.addWidget(self.code_tableau)

        self.copier_code = wx.Button(self, label = u"Copier dans le presse-papier")
        self.bsizer.addWidget(self.copier_code)

        self.bsizer.addWidget(QLabel(u"Pensez � rajouter dans l'ent�te de votre fichier LaTeX la ligne suivante :", self))

        self.sizer_entete = QHBoxLayout()
        self.code_entete = wx.TextCtrl(self, size = (200, -1), value = u"\\usepackage{tabvar}", style = wx.TE_READONLY)
        self.sizer_entete.addWidget(self.code_entete)
        self.copier_entete = wx.Button(self, label = u"Copier cette ligne")
        self.sizer_entete.addWidget(self.copier_entete)

        self.bsizer.addLayout(self.sizer_entete)

        self.sizer.addLayout(self.bsizer)


        self.cb = QCheckBox(self, label = u"Copier automatiquement le code LaTeX dans le presse-papier.")
        self.cb.setChecked(self._param_.copie_automatique)
        self.sizer.addWidget(self.cb)

        self.setLayout(self.sizer)
        self.adjustSize()

        self.type_tableau.Bind(wx.EVT_CHOICE, self.EvtChoix)
        self.EvtChoix()

        def copier_code(event = None):
            self.vers_presse_papier(texte = self.code_tableau.GetValue())
        self.copier_code.Bind(wx.EVT_BUTTON, copier_code)

        def copier_entete(event = None):
            self.vers_presse_papier(texte = self.code_entete.GetValue())
        self.copier_entete.Bind(wx.EVT_BUTTON, copier_entete)

        def regler_mode_copie(event = None):
            self._param_.copie_automatique = self.cb.GetValue()
        self.cb.Bind(wx.EVT_CHECKBOX, regler_mode_copie)

        def regler_cellspace(event = None):
            self._param_.utiliser_cellspace = self.utiliser_cellspace.GetValue()
            if self._param_.utiliser_cellspace:
                self.code_entete.setText(u"\\usepackage{cellspace}")
            else:
                self.code_entete.setText(u"")
        self.utiliser_cellspace.Bind(wx.EVT_CHECKBOX, regler_cellspace)

        def regler_derivee(event = None):
            self._param_.derivee = self.derivee.GetValue()
        self.derivee.Bind(wx.EVT_CHECKBOX, regler_derivee)

        def regler_limites(event = None):
            self._param_.limites = self.limites.GetValue()
        self.limites.Bind(wx.EVT_CHECKBOX, regler_limites)

    def activer(self):
        # Actions � effectuer lorsque l'onglet devient actif
        self.entree.setFocus()

    def vers_presse_papier(self, event = None, texte = ""):
        Panel_simple.vers_presse_papier(texte)


    def generer_code(self, commande, **kw):
        self.modifie = True
        try:
            if self._param_.mode == 0:
                code_latex = tabvar(commande, derivee=self._param_.derivee, limites=self._param_.limites)
            elif self._param_.mode == 1:
                code_latex = tabsign(commande, cellspace=self._param_.utiliser_cellspace)
            elif self._param_.mode == 2:
                code_latex = tabval(commande)
            else:
                warning("Type de tableau non reconnu.")

            self.code_tableau.setText(code_latex)
            if self._param_.copie_automatique:
                self.vers_presse_papier(texte = code_latex)
            self.entree.setFocus()
            self.message(u"Le code LaTeX a bien �t� g�n�r�.")
        except BaseException, erreur:
            self.message(u"Impossible de g�n�rer le code LaTeX. " + message(erreur))
            self.entree.setFocus()
            if param.debug:
                raise






    def EvtChoix(self, event = None):
        self._param_.mode = self.type_tableau.GetSelection()
        if self._param_.mode == 0:
            self.code_entete.setText(u"\\usepackage{tabvar}")
            self.entree.setToolTip(tabvar.__doc__)
            self.utiliser_cellspace.setEnabled(False)
            self.derivee.setEnabled(True)
            self.limites.setEnabled(True)
        elif self._param_.mode == 1:
            self.utiliser_cellspace.setEnabled(True)
            self.derivee.setEnabled(False)
            self.limites.setEnabled(False)
            self.entree.setToolTip(tabsign.__doc__)
            if self._param_.utiliser_cellspace:
                self.code_entete.setText(u"\\usepackage{cellspace}")
            else:
                self.code_entete.setText(u"")
        elif self._param_.mode == 2:
            self.utiliser_cellspace.setEnabled(False)
            self.derivee.setEnabled(False)
            self.limites.setEnabled(False)
            self.entree.setToolTip(tabval.__doc__)
            self.code_entete.setText(u"")
