"""
@author: loblum
unimod avg = mono * 1.001191917
"""
from string import Template


def modstr_to_engine(static_modstr, var_modstr, engine):
    if engine is "XTandem":
        conv = XTandemModConverter()
    elif engine is "Omssa":
        conv = OmssaModConverter()
    elif engine is "Myrimatch":
        conv = MyrimatchModConverter()
    elif engine is "Comet":
        conv = CometModConverter()
    else:
        raise Exception("No converter found for engine " + engine)

    try:
        return conv.modlist_to_engine(static_modstr, var_modstr)
    except Exception, e:
        raise Exception("Malformed modification string! "+e.message)


def _get_mass_from_unimod_or_string(key):
    from Unimod.unimod import database

    entry = database.get_label(key)
    if entry:
        return float(entry['delta_mono_mass']), float(entry['delta_avge_mass'])
    else:
        #if its not a unimod entry try to parse masses from name itself
        try:
            mm, am = key.split("/")
            return float(mm), float(am)
        except:
            raise Exception(key + ": not found unimod and no valid mono/avg mass pair")


def _modstr_to_list(modstr):
    modlist = []
    for mod in modstr.split(";"):
        if not mod: return modlist
        name, residues = mod.split(" ")
        mono, avg = _get_mass_from_unimod_or_string(name)
        residuesarr = list(residues)[1:-1]
        if len(residuesarr) < 1: raise Exception("Could not get residues in string "+residues)
        modlist.append([name, mono, avg, residuesarr])
    return modlist


class AbstractModConverter(object):
    def modlist_to_engine(static_modstr, var_modstr):
        raise NotImplementedError


class XTandemModConverter(AbstractModConverter):
    def modlist_to_engine(self, static_modstr, var_modstr):
        smods = []
        for mod in _modstr_to_list(static_modstr):
            name, mono, avg, residues = mod
            for residue in residues:
                smods.append("%f@%s" % (mono, residue))

        vmods = []
        for mod in _modstr_to_list(var_modstr):
            name, mono, avg, residues = mod
            for residue in residues:
                vmods.append("%f@%s" % (mono, residue))

        return ",".join(smods), ",".join(vmods), None


class OmssaModConverter(AbstractModConverter):
    __tplheader = """<?xml version="1.0"?>
<MSModSpecSet
    xmlns="http://www.ncbi.nlm.nih.gov"
    xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
    xs:schemaLocation="http://www.ncbi.nlm.nih.gov OMSSA.xsd"
>"""
    __tpl = """<MSModSpec>
    <MSModSpec_mod>
      <MSMod value="usermod$I">$NUM</MSMod>
    </MSModSpec_mod>
    <MSModSpec_type>
      <MSModType value="modaa">0</MSModType>
    </MSModSpec_type>
    <MSModSpec_name>$NAME</MSModSpec_name>
    <MSModSpec_monomass>$MONOMASS</MSModSpec_monomass>
    <MSModSpec_averagemass>$AVGMASS</MSModSpec_averagemass>
    <MSModSpec_n15mass>0</MSModSpec_n15mass>
    <MSModSpec_residues>
      <MSModSpec_residues_E>$RESIDUE</MSModSpec_residues_E>
    </MSModSpec_residues>
  </MSModSpec>"""
    __tpltail = """</MSModSpecSet>"""

    def modlist_to_engine(self, static_modstr, var_modstr):
        modtpl = self.__tplheader
        i = 0
        smods = []
        for mod in _modstr_to_list(static_modstr):
            name, mono, avg, residues = mod
            for res in residues:
                i += 1
                if i > 9: raise Exception("For Omssa only up to 10 modifications are suported")
                no = i + 118
                smods.append(str(no))
                dict_ = {"I": i, "NUM": no, "NAME": name, "MONOMASS": mono, "AVGMASS": avg, "RESIDUE": res}
                modtpl += Template(self.__tpl).safe_substitute(dict_)

        vmods = []
        for mod in _modstr_to_list(var_modstr):
            name, mono, avg, residues = mod
            for res in residues:
                i += 1
                if i > 9: raise Exception("For Omssa only up to 10 modifications are suported")
                no = i + 118
                vmods.append(str(no))
                dict_ = {"I": i, "NUM": no, "NAME": name, "MONOMASS": mono, "AVGMASS": avg, "RESIDUE": res}
                modtpl += Template(self.__tpl).safe_substitute(dict_)

        modtpl += self.__tpltail
        return ",".join(smods), ",".join(vmods), modtpl


class MyrimatchModConverter(AbstractModConverter):
    def modlist_to_engine(self, static_modstr, var_modstr):
        smods = []
        for mod in _modstr_to_list(static_modstr):
            name, mono, avg, residues = mod
            for residue in residues:
                smods.append("%s %f" % (residue, mono))

        vmods = []
        for mod in _modstr_to_list(var_modstr):
            name, mono, avg, residues = mod
            vmods.append("[%s] * %f" % ("".join(residues), mono))

        return " ".join(smods), " ".join(vmods), None


class CometModConverter(AbstractModConverter):
    __fullnames = {"A": "alanine", "C": "cysteine", "D": "aspartic_acid", "E": "glutamic_acid", "F": "phenylalanine",
                   "G": "glycine", "H": "histidine", "I": "isoleucine", "K": "lysine", "L": "leucine",
                   "M": "methionine", "N": "asparagine", "O": "ornithine", "P": "proline", "Q": "glutamine",
                   "R": "arginine", "S": "serine", "T": "threonine", "V": "valine", "W": "tryptophan",
                   "Y": "tyrosine", }

    def modlist_to_engine(self, static_modstr, var_modstr):
        smods = ""
        for mod in _modstr_to_list(static_modstr):
            name, mono, avg, residues = mod
            for residue in residues:
                try:
                    smods += "add_%s_%s = %f\n" % (residue, self.__fullnames[residue], mono)
                except KeyError, e:
                    raise Exception("Residue "+e.message+" not known")

        vmods = ""
        for i, mod in enumerate(_modstr_to_list(var_modstr)):
            if i > 5: raise Exception("Comet only supports up to 6 variable mods")
            name, mono, avg, residues = mod
            vmods += "variable_mod%s = %f %s 0 3\n" % (i + 1, mono, "".join(residues))

        return smods, vmods, None
