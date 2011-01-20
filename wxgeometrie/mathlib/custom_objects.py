#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2010  Nicolas Pourcelot
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# version unicode

## Objets compl�mentaires � ceux de sympy

import re, math, types

import sympy, numpy
#~ import end_user_functions
from sympy.printing.latex import LatexPrinter
from sympy.printing.str import StrPrinter

from internal_objects import ObjetMathematique
import custom_functions
import sympy_functions
import mathlib
import pylib
import parsers
import param

class Fonction(ObjetMathematique):
    def __init__(self, variables, expression):
        if not isinstance(variables, (list, tuple)):
            variables = (variables,)
        self.variables = variables
        self.expression = expression

    @classmethod
    def _substituer(cls, expression, dico):
        if hasattr(expression, "__iter__"):
            return expression.__class__(cls._substituer(elt, dico) for elt in expression)
        return expression.subs(dico)

    def __call__(self, *args, **kw):
        if kw:
            if args:
                raise ArgumentError, "les arguments sont entres de deux facons differentes."
            return self._substituer(self.expression, [(sympy.Symbol(key), value) for key, value in kw.iteritems()])
        if len(args) > len(self.variables):
            raise ArgumentError, "il y a plus d'arguments que de variables."
        return self._substituer(self.expression, zip(self.variables[:len(args)], args))

    def _variables(self):
        return tuple(str(arg) for arg in self.variables)

    def __str__(self):
        return ", ".join(self._variables()) + " -> " + str(self.expression)

    def __repr__(self):
        return "Fonction(%s, %s)" %(repr(self.variables), repr(self.expression))

    for op in ("add", "mul", "div", "rdiv", "pow", "rpow"):
        op = "__" + op + "__"
        def __op__(self, y, op = op):
            if isinstance(y, Fonction):
                if self.variables == y.variables or not y.variables:
                    return Fonction(self.variables, getattr(self.expression, op)(y.expression),)
                elif not self.variables:
                    return Fonction(y.variables, getattr(self.expression, op)(y.expression),)
                else:
                    raise ValueError, "les deux fonctions n'ont pas les memes variables."
            else:
                return Fonction(self.variables, getattr(self.expression, op)(y),)
        exec("%s=__op__" %op)
    del __op__

    def __ne__(self):
        return Fonction(self.variables, -self.expression)

    def __abs__(self):
        return Fonction(self.variables, abs(self.expression))

    def __eq__(self, y):
        if isinstance(y, Fonction):
            return self.expression == y.expression
        else:
            return self.expression == y

    def __gt__(self, y):
        if isinstance(y, Fonction):
            return self.expression > y.expression
        else:
            return self.expression > y


class Matrice(sympy.Matrix):
    def __repr__(self):
        return "Matrice(%s)" %repr(self.mat)


class ProduitEntiers(long):
    u"""Usage interne : destin� � �tre utilis� avec sympy.factorint."""

    def __new__(cls, *couples):
        val = 1
        for (m, p) in couples:
            val *= m**p
        self = long.__new__(cls, val)
        self.couples = couples
        return self

#    __slots__ = ["couples"]

    def __str__(self):
        def formater(exposant):
            if exposant == 1:
                return ""
            return "**" + str(exposant)
        return "*".join((str(entier) + formater(exposant)) for entier, exposant in self.couples)

    def __repr__(self):
        return "ProduitEntiers(*%s)" %repr(self.couples)




#TODO: cr�er une classe Wrapper, dont MesureDegres doit h�riter,
# Note: this must wrap all special methods
# http://docs.python.org/reference/datamodel.html#more-attribute-access-for-new-style-classes
class MesureDegres(pylib.GenericWrapper):
    u"""Usage interne : destin� � �tre utilis� avec custom_functions.deg."""

    __slots__ = ('__val',)

    def __str__(self):
        return str(self.__val) + '�'

    def __repr__(self):
        return repr(self.__val) + '�'

    def __unicode__(self):
        return unicode(self.__val) + u'�'





class Temps(object):
    def __init__(self, secondes = 0, **kw):
        self.secondes = secondes + kw.get("s", 0) \
                                                + 60*kw.get("m", 0) + 60*kw.get("min", 0) \
                                                + 3600*kw.get("h", 0) \
                                                + 86400*kw.get("j", 0) + 86400*kw.get("d", 0)

    def jhms(self):
        s = float(self.secondes)
        s, dec = int(s), s-int(s)
        j, s = s//86400, s%86400
        h, s = s//3600, s%3600
        m, s = s//60, s%60
        return j, h, m, s + dec

    def __str__(self):
        return  "%s j %s h %s min %s s" %self.jhms()

    def __repr__(self):
        return "Temps(%s)" %self.secondes


class CustomStrPrinter(StrPrinter):
    def _print_str(self, expr):
        return '"%s"' %expr.replace('"', r'\"')

    def _print_unicode(self, expr):
        return '"%s"' %expr.replace('"', r'\"')

    def _print_Exp1(self, expr):
        return 'e'

    def _print_ImaginaryUnit(self, expr):
        return 'i'

    def _print_Infinity(self, expr):
        return '+oo'

    def _print_log(self, expr):
        return "ln(%s)"%self.stringify(expr.args, ", ")

    def _print_Pow(self, expr):
        precedence = sympy.printing.precedence.precedence
        PREC = precedence(expr)
        if expr.exp.is_Rational and expr.exp.p == 1 and expr.exp.q == 2:
            return 'sqrt(%s)' % self._print(expr.base)
        if expr.exp.is_Rational and expr.exp.is_negative:
            return '1/%s'%self._print(expr.base**abs(expr.exp))
        else:
            return '%s^%s'%(self.parenthesize(expr.base, PREC),
                             self.parenthesize(expr.exp, PREC))

    def _print_Real(self, expr):
        string = StrPrinter._print_Real(self, expr)
        return string.replace('e+', '*10^').replace('e-', '*10^-')

    def doprint(self, expr):
        return StrPrinter.doprint(self, expr) if not isinstance(expr, unicode) else expr



class CustomLatexPrinter(LatexPrinter):
    def __init__(self, profile = None):
        _profile = {
            "mat_str" : "pmatrix",
            "mat_delim" : "",
            "descending": True,
            "mode": "inline",
        }
        if profile is not None:
            _profile.update(profile)
        LatexPrinter.__init__(self, _profile)

    def _print_Temps(self, expr):
        return r"%s \mathrm{j}\, %s \mathrm{h}\, %s \mathrm{min}\, %s \mathrm{s}" %expr.jhms()

    def _print_exp(self, expr, exp=None):
        tex = r"\mathrm{e}^{%s}" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)

    def _print_Exp1(self, expr):
        return r"\mathrm{e}"

    def _print_ImaginaryUnit(self, expr):
        return r"\mathrm{i}"

    def _print_Fonction(self, expr):
        return ", ".join(expr._variables()) + "\\mapsto " + self._print(expr.expression)

    def _print_Function(self, expr, exp=None):
        func = expr.func.__name__

        if hasattr(self, '_print_' + func):
            return getattr(self, '_print_' + func)(expr, exp)

        else:
            if exp is not None:
                name = r"\mathrm{%s}^{%s}" % (func, exp)
            else:
                name = r"\mathrm{%s}" % func
            if len(expr.args) == 1 and isinstance(expr.args[0], (sympy.Symbol, sympy.Integer)):
                return name + "(" + str(self._print(expr.args[0])) +")"
            else:
                args = [ str(self._print(arg)) for arg in expr.args ]
                return name + r"\left(%s\right)" % ",".join(args)

    def _print_ProduitEntiers(self, expr):
        def formater(exposant):
            if exposant == 1:
                return ""
            return "^" + str(exposant)
        return "\\times ".join((str(entier) + formater(exposant)) for entier, exposant in expr.couples)

    def _print_Real(self, expr):
        s = str(expr)
        if "e" in s:
            nombre,  exposant = s.split("e")
            return nombre + "\\times 10^{" + exposant.lstrip("+") + "}"
        else:
            return s

    def _print_Infinity(self, expr):
        return r"+\infty"

    def _print_Order(self, expr):
        return r"\mathcal{O}\left(%s\right)" % \
            self._print(expr.args[0])

    def _print_abs(self, expr, exp=None):
        tex = r"\left|{%s}\right|" % self._print(expr.args[0])

        if exp is not None:
            return r"%s^{%s}" % (tex, exp)
        else:
            return tex

    def _print_Union(self, expr):
        tex = r"\cup".join(self._print(intervalle) for intervalle in expr.intervalles)
        tex = tex.replace(r"\}\cup\{", "\,;\, ")
        return tex

    def _print_Intervalle(self, expr):
        if expr.vide:
            return r"\varnothing"
        elif expr.inf_inclus and expr.sup_inclus and expr.inf == expr.sup:
            return r"\{%s\}" % self._print(expr.inf)
        if expr.inf_inclus:
            left = "["
        else:
            left = "]"
        if expr.sup_inclus:
            right = "]"
        else:
            right = "["
        return r"%s%s;%s%s" % (left, self._print(expr.inf), self._print(expr.sup), right)

    def _print_Singleton(self, expr):
        return r"\{%s\}" % self._print(expr.inf)

    def _print_tuple(self, expr):
        return "(" + ",\,".join(self._print(item) for item in expr) + ")"

    def _print_log(self, expr, exp=None):
        if len(expr.args) == 1 and isinstance(expr.args[0], (sympy.Symbol, sympy.Integer)):
            tex = r"\ln(%s)" % self._print(expr.args[0])
        else:
            tex = r"\ln\left(%s\right)" % self._print(expr.args[0])
        return self._do_exponent(tex, exp)


    def _print_Add(self, expr):
        if self._settings["descending"]:
            args = list(expr.args)
            args.sort(sympy.Basic._compare_pretty, reverse = True)
            tex = str(self._print(args[0]))
            for term in args[1:]:
                coeff = term.as_coeff_terms()[0]
                if coeff.is_negative:
                    tex += r" %s" % self._print(term)
                else:
                    tex += r" + %s" % self._print(term)
            return tex

        return LatexPrinter._print_Add(self, expr)

    def _print_function(self, expr):
        return r"\mathrm{Fonction}\, " + expr.func_name


class LocalDict(dict):
    globals = {}
##    def __getitem__(self, name):
##        #~ print "Nom de clef: ", name
##        #~ print "local: ", self.has_key(name)
##        #~ print "global: ", self.globals.has_key(name)
##        if self.has_key(name) or self.globals.has_key(name): # doit renvoyer une KeyError si la cl� est dans le dictionnaire global, pour que Python y aille chercher ensuite la valeur associ�e � la cl�
##            return dict.__getitem__(self, name)
##        return sympy.Symbol(name)

    def __missing__(self, key):
        return self.globals.get(key, sympy.Symbol(key))

    def __setitem__(self, name, value):
        # Pour �viter que l'utilisateur red�finisse pi, i, e, etc. par m�garde.
        if self.globals.has_key(name):
            raise NameError, "%s est un nom reserve" %name
        if isinstance(value, str):
            # exec/eval encodent les cha�nes cr�es en utf8.
            value = value.decode("utf8").encode(param.encodage)
        # [[1,2],[3,4]] est converti en une matrice
        if isinstance(value, list) and len(value):
            if isinstance(value[0], list):
                n = len(value[0])
                test = True
                for elt in value[1:]:
                    if not isinstance(elt, list) or len(elt) != n:
                        test = False
                        break
                if test:
                    value = sympy_functions.mat(value)
        dict.__setitem__(self, name, value)




class Interprete(object):
    def __init__(self,  calcul_exact = True,
                        ecriture_scientifique = False,
                        forme_algebrique = True,
                        simplifier_ecriture_resultat = True,
                        changer_separateurs = False,
                        separateurs_personnels = (",", ";"),
                        copie_automatique = False,
                        formatage_OOo = True,
                        formatage_LaTeX = True,
                        ecriture_scientifique_decimales = 2,
                        precision_calcul = 60,
                        precision_affichage = 18,
                        simpify = True,
                        verbose = None,
                        appliquer_au_resultat = None,
                        inversion_addition_LaTeX = False,
                        ):
        # Dictionnaire local (qui contiendra toutes les variables d�finies par l'utilisateur).
        self.locals = LocalDict()
        # Dictionnaire global (qui contient les fonctions, variables et constantes pr�d�finies).
        self.globals = vars(mathlib.end_user_functions).copy()
        self.globals.update({
                "__builtins__": None,
                "Fonction": Fonction,
                "Matrice": Matrice,
                "Temps": Temps,
                "ProduitEntiers": ProduitEntiers,
                "Ensemble": mathlib.intervalles.Ensemble,
                "__sympify__": sympy.sympify,
                "ans": self.ans,
                "rep": self.ans, # alias en fran�ais :)
                "__vars__": self.vars,
#                "__decimal__": Decimal,
                "__decimal__": self._decimal,
                "__local_dict__": self.locals,
                "range": numpy.arange,
                "arange": numpy.arange,
                            })
        # pour �viter que les proc�dures de r��criture des formules ne touchent au mots clefs,
        # on les r�f�rence comme fonctions (elles seront inaccessibles, mais ce n'est pas grave).
        # ainsi, "c and(a or b)" ne deviendra pas "c and*(a or b)" !
        # self.globals.update({}.fromkeys(pylib.securite.keywords_autorises, lambda:None))

        # On import les fonctions python qui peuvent avoir une utilit� �ventuel (et ne pr�sentent pas de probl�me de s�curit�)
        a_importer = ['all', 'unicode', 'isinstance', 'dict', 'oct', 'sorted', 'list', 'iter', 'set', 'reduce', 'issubclass', 'getattr', 'hash', 'len', 'frozenset', 'ord', 'filter', 'pow', 'float', 'divmod', 'enumerate', 'basestring', 'zip', 'hex', 'chr', 'type', 'tuple', 'reversed', 'hasattr', 'delattr', 'setattr', 'str', 'int', 'unichr', 'any', 'min', 'complex', 'bool', 'max', 'True', 'False']

        for nom in a_importer:
            self.globals[nom] = __builtins__[nom]

        self.locals.globals = self.globals

        # gerer les fractions et les racines de maniere exacte si possible.
        self.calcul_exact = calcul_exact
        # afficher les resultats en ecriture scientifique.
        self.ecriture_scientifique = ecriture_scientifique
        # mettre les r�sultats complexes sous forme alg�brique
        self.forme_algebrique = forme_algebrique
        # �crire le r�sultat sous une forme plus agr�able � lire
        # (suppression des '*' dans '2*x', etc.)
        self.simplifier_ecriture_resultat = simplifier_ecriture_resultat
        # appliquer les s�parateurs personnalis�s
        self.changer_separateurs = changer_separateurs
        # s�parateurs personnalis�s (s�parateur d�cimal, s�parateur de listes)
        self.separateurs_personnels = separateurs_personnels
        # d'autres choix sont possibles, mais pas forc�ment heureux...
        # copie automatique de chaque r�sultat dans le presse-papier
        self.copie_automatique = copie_automatique
        self.formatage_OOo = formatage_OOo
        self.formatage_LaTeX = formatage_LaTeX
        self.ecriture_scientifique_decimales = ecriture_scientifique_decimales
        self.precision_calcul = precision_calcul
        self.precision_affichage = precision_affichage
        self.verbose = verbose
        self.simpify = simpify
        # une fonction � appliquer � tous les r�sultats
        self.appliquer_au_resultat = appliquer_au_resultat
        # inverser l'ordre d'affichage des termes d'une somme
        self.inversion_addition_LaTeX = inversion_addition_LaTeX
        self.latex_dernier_resultat = ''
        self.initialiser()

    def _decimal(self, nbr, prec = None):
        if prec is None:
            prec = self.precision_calcul
        return sympy.Real(nbr, prec)

    def initialiser(self):
        self.locals.clear()
        self.derniers_resultats = []

    def evaluer(self, calcul = ""):
        self.warning = ""
        # calcul = re.sub("[_]+", "_", calcul.strip()) # par mesure de s�curit�, les "__" sont interdits.
        # Cela permet �ventuellement d'interdire l'acc�s � des fonctions.
        # Warning: inefficace. Cf. "_import _builtins_import _

        # Ferme automatiquement les parentheses.
        parentheses = "({[", ")}]"
        for i in range(3):
            difference = calcul.count(parentheses[0][i])-calcul.count(parentheses[1][i])
            if difference > 0:
                calcul += difference*parentheses[1][i]
                self.warning += u" Attention, il manque des parenth�ses \"" + parentheses[1][i] + "\"."
            elif difference < 0:
                self.warning += u" Attention, il y a des parenth�ses \"" + parentheses[1][i] + "\" superflues."
                if calcul.endswith(abs(difference)*parentheses[1][i]):
                    calcul = calcul[:difference]

##        # Transforme les ' en ` et les " en ``
##        calcul = calcul.replace("'", "`").replace('"', '``')

        if self.verbose:
            print "Traitement ({[]}) :  ", calcul

        if calcul and calcul[0] in "><!=^*/%+":
            calcul = "_" + calcul

        if self.verbose:
            print "Traitement ><!=^*/%+ :  ", calcul

        if self.formatage_LaTeX and calcul.rstrip().endswith("\\approx"):
            calcul = calcul.rstrip()[:-7] + ">>evalf"

        if ">>" in calcul:
            liste = calcul.split(">>")
            calcul = liste[0]
            for s in liste[1:]:
                calcul = s + "(" + calcul + ")"

        if self.verbose:
            print "Traitement >> :  ", calcul

        try:
            param.calcul_approche = not self.calcul_exact
            # utilis� en particulier dans la factorisation des polyn�mes
            self._executer(calcul)
        except Exception:
            # Si le calcul �choue, c'est peut-�tre que l'utilisateur a utilis� une virgule pour les d�cimaux
            sep = self.separateurs_personnels[0]
            _raise = True
            if not self.changer_separateurs and re.search(r'\d[' + sep + r']\d', calcul):
                self.changer_separateurs = True
                try:
                    # On retente le calcul apr�s avoir d�fini la virgule comme s�parateur d�cimal
                    self._executer(calcul)
                    self.warning += u" Attention: s�parateur d�cimal incorrect."
                    _raise = False
                finally:
                    self.changer_separateurs = False
            if _raise:
                raise
        finally:
            param.calcul_approche = False

        self.derniers_resultats.append(self.locals["_"])

        if not self.calcul_exact:
            return self._formater(sympy_functions.evalf(self.locals["_"], self.precision_calcul))
        return self._formater(self.locals["_"])


    def _ecriture_scientifique(self, chaine):
        valeur = float(chaine)
        mantisse = int(math.floor(math.log10(abs(valeur))))
        chaine = str(round(valeur/10.**mantisse, self.ecriture_scientifique_decimales))
        if mantisse:
            chaine += "*10^"+str(mantisse)
        return  chaine

    def _ecriture_scientifique_latex(self, chaine):
        valeur = float(chaine)
        mantisse = int(math.floor(math.log10(abs(valeur))))
        chaine = str(round(valeur/10.**mantisse, self.ecriture_scientifique_decimales))
        if mantisse:
            chaine += "\\times 10^{%s}" %mantisse
        return  chaine




    def _formater_decimaux(self, chaine):
        if "." in chaine:
            chaine = str(sympy.Real(str(chaine), self.precision_calcul).evalf(self.precision_affichage))
            chaine = chaine.rstrip('0')
            if chaine.endswith("."):
                chaine = chaine[:-1]
        return chaine






    def _formater(self, valeur):
##        resultat = self._formatage_simple(valeur)
        resultat = mathlib.custom_functions.custom_str(valeur)
        if valeur is None:
            latex = ""
        else:
            profile = {'descending': self.inversion_addition_LaTeX}
            try:
                latex = mathlib.custom_functions.custom_latex(valeur, profile)
            except Exception:
                pylib.print_error()
                latex = ''



        if self.ecriture_scientifique and not self.calcul_exact:
            resultat = pylib.regsub(parsers.NBR, resultat, self._ecriture_scientifique)
            latex = pylib.regsub(parsers.NBR, latex, self._ecriture_scientifique_latex)
        else:
##            print "initial", resultat
            resultat = pylib.regsub(parsers.NBR, resultat, self._formater_decimaux)
##            print "final", resultat
            latex = pylib.regsub(parsers.NBR, latex, self._formater_decimaux)

##        if re.match("[0-9]*[.][0-9]+$", resultat):
##            resultat = resultat.rstrip('0')
##            if resultat.endswith("."):
##                resultat += "0"
##            latex = "$" + resultat + "$"
        if self.changer_separateurs:
            resultat = resultat.replace(",", self.separateurs_personnels[1]).replace(".", self.separateurs_personnels[0])
            latex = latex.replace(",", self.separateurs_personnels[1]).replace(".", self.separateurs_personnels[0])

        self.latex_dernier_resultat = latex
        if self.simplifier_ecriture_resultat:
            resultat = parsers.simplifier_ecriture(resultat)
        return resultat, latex


    def _traduire(self, formule):
        variables = self.globals.copy()
        variables.update(self.locals)
        #callable_types = (  types.BuiltinFunctionType,
                            #types.BuiltinMethodType,
                            #types.FunctionType,
                            #types.UfuncType,
                            #types.MethodType,
                            #types.TypeType,
                            #types.ClassType)
        #fonctions = [key for key, val in variables.items() if isinstance(val, callable_types)]
##        fonctions = [key for key, val in variables.items() if hasattr(val, "__call__") and not isinstance(val, sympy.Atom)]
        #print fonctions
        # La fonction traduire_formule de la librairie mathlib.formatage permet d'effectuer un certain nombre de conversions.
        formule = parsers.traduire_formule(formule, fonctions = variables,
                        OOo = self.formatage_OOo,
                        LaTeX = self.formatage_LaTeX,
                        changer_separateurs = self.changer_separateurs,
                        separateurs_personnels = self.separateurs_personnels,
                        simpify = self.simpify,
                        verbose = self.verbose,
                        )

        formule = re.sub("(?<![A-Za-z0-9_])(resous|solve)", "resoudre", formule)
        i = formule.find("resoudre(")
        if i != -1:
            while formule.find("(et)") != -1:
                formule = formule.replace("(et)", "et")
            while formule.find("(ou)") != -1:
                formule = formule.replace("(ou)", "ou")
            formule = formule.replace("*ou*", " ou ").replace("*et*", " et ")\
                        .replace("*ou-", " ou -").replace("*et-", " et -")\
                        .replace("*ou+", " ou +").replace("*et+", " et +")
            deb, bloc, fin = pylib.split_around_parenthesis(formule, i)
            formule = deb + '("' + bloc[1:-1] + '", local_dict = __local_dict__)'
        if self.verbose or (self.verbose is None and param.debug):
            print "test_resoudre: ", i, formule
        return formule


    def _executer(self, instruction):
        # Cas d'une fonction.
        # Exemple: 'f(x,y)=x+y+3' sera traduit en 'f=Fonction((x,y), x+y+3)'
        if re.match("[^=()]+[(][^=()]+[)][ ]*=[^=]", instruction):
            var, val = instruction.split("=", 1)
            var = var.strip()
            i = var.find("(")
            nom = var[:i]
            variables = var[i:]
            instruction = nom + "=Fonction(" + variables + "," + self._traduire(val) + ")"
        else:
            instruction = self._traduire(instruction)

        # dans certains cas, il ne faut pas affecter le r�sultat � la variable "_" (cela provoquerait une erreur de syntaxe)
        # (Mots cl�s devant se trouver en d�but de ligne : dans ce cas, on ne modifie pas la ligne)
##        if True in [instruction.startswith(exception + " ") for exception in securite.__keywords_debut_ligne__]:
##        def re_keywords(liste):
##            global pylib
##            return "("+"|".join(pylib.securite.keywords_debut_ligne)+")[ :(;'\"]"

##        if re.match(re_keywords(pylib.securite.keywords_debut_ligne), instruction):
##            self.locals["_"] = None
##        else:
##            instruction = "_=" + instruction

        if pylib.securite.expression_affectable(instruction):
            instruction = "_=" + instruction
        else:
            self.locals["_"] = None

##        keywords_interdits = [kw + " " for kw in securite.__keywords_interdits__] + [kw + "(" for kw in securite.__keywords_interdits__]
##        instruction = recursive_mreplace(instruction, keywords_interdits)
        if pylib.securite.keywords_interdits_presents(instruction):
            self.warning += 'Les mots-clefs ' + ', '.join(sorted(pylib.securite.keywords_interdits)) \
                            + ' sont interdits.'
            raise RuntimeError, "Mots-clefs interdits."
##        pylib.regsub(re_keywords(pylib.securite.keywords_interdits), instruction, " ")

        #print self.globals.keys()
        try:
            exec(instruction, self.globals, self.locals)
        except NotImplementedError:
            pylib.print_error()
            self.locals["_"] = "?"
        if self.forme_algebrique and isinstance(self.locals["_"], sympy.Basic) and hasattr(self.locals["_"], "is_number") and self.locals["_"].is_number:
            try:
                real, imag = self.locals["_"].as_real_imag()
                self.locals["_"] = real + sympy.I*imag
            except NotImplementedError:
                pylib.print_error()
        if self.appliquer_au_resultat is not None:
            self.locals["_"] = self.appliquer_au_resultat(self.locals["_"])


    def vars(self):
        dictionnaire = self.globals.copy()
        dictionnaire.update(self.locals)
        return dictionnaire


    def ans(self, n = -1):
        if n >= 0:
            n = int(n-1)
        else:
            n = int(n)
        if self.derniers_resultats: return self.derniers_resultats[n]
        self.warning += u" Ans(): aucun calcul ant�rieur."
        return 0

    def clear_state(self):
        self.locals.clear()

    def save_state(self):
        def repr2(expr):
            if isinstance(expr, (types.BuiltinFunctionType, types.TypeType, types.FunctionType)):
                return expr.__name__
            return repr(expr)
        return '\n'.join(k + ' = ' + repr2(v) for k, v in self.locals.items()) \
                + '\n\n@derniers_resultats = [\n    ' + '\n    '.join(repr(repr2(res)) +',' for res in self.derniers_resultats) + '\n    ]'

    def load_state(self, state):
        def evaltry(expr):
            u"Evalue l'expression. En cas d'erreur, intercepte l'erreur et retourne None."
            try:
                return eval(expr, self.globals, self.locals)
            except Exception:
                print("Error: l'expression suivante n'a pu �tre �valu�e par l'interpr�te: %s." %repr(expr))
                pylib.print_error()

        self.clear_state()
        etat_brut, derniers_resultats = state.split('@derniers_resultats = ', 1)
        etat = (l.split(' = ', 1) for l in etat_brut.split('\n') if l)
        self.locals.update((k, evaltry(v)) for k, v in etat)
        liste_repr = eval(derniers_resultats, self.globals, self.locals)
        self.derniers_resultats = [evaltry(s) for s in liste_repr]
