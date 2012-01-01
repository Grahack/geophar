MODULES
_______

Ce r�pertoire contient tous les modules de WxG�om�trie.

L'activation d'un module au d�marrage de WxG�om�trie d�pend de sa pr�sence dans param.__init__.py
Pour activer/d�sactiver des modules, �ditez ce fichier avec un �diteur de texte, et modifiez la ligne :
modules = ("geometre", "traceur", "statistiques", "calculatrice", "probabilites", "surfaces")

Un fichier description.py permet d'int�grer le module dans l'installeur pour Windows.
Depuis la version 0.131, un module n'est pas reconnu si ce fichier est absent.

Format du fichier description.py :
----------------------------------
# titre : description sommaire du module
# description : description d�taill�e
# defaut : par d�faut, le module est-il install� ou non ?
# groupe : "Modules" pour tous les modules
defaut peut valoir True, False ou None.
(None signifie que le module est n�cessairement install�)

Exemple de fichier 'description.py':

# -*- coding: iso-8859-1 -*-
description = {
"titre":                    u"Calculatrice",
"description":              u"Calculatrice avanc�e orient�e math�matiques destin�e au coll�ge/lyc�e.",
"groupe":                   u"Modules",
"defaut":  True,
}


Pour plus de d�tails concernant la cr�ation de nouveaux modules pour WxG�om�trie, voir :
doc/developpeurs/documentation de l'API.pdf
