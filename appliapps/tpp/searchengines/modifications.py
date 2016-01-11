import re
from string import Template
from Unimod.unimod import database


def genmodstr_to_engine(static_genmodstr, var_genmodstr, engine):
    """
    Main method you should use this
    Converts "generic" modification string into engine specific strings
    unimod avg = mono * 1.001191917

    @param static_genmodstr: generic mod string for static modifications to use
    @param var_genmodstr: generic mod string for variable modifications to use
    @param engine: search engine

    @return: engine_specific_static_mod_string, engine_specific_variable_mod_string, template(omssa)
    """
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
        return conv.genmodstrs_to_engine(static_genmodstr, var_genmodstr)
    except Exception, e:
        raise Exception("Malformed modification string! " + e.message)


class AbstractModConverter(object):
    def genmodstrs_to_engine(self, static_genmodstr, var_genmodstr):
        """
        Method to overwrite in child classes. Is expected to convert generic modification strings to engine
        specifig strings

        @param static_genmodstr: generic mod string for static
        @param var_genmodstr: generic mod string for variable
        @return static_mods, var_mods, template(needed e.g. for omssa)
        """
        raise NotImplementedError

    def _get_nameresiduelist_from_modstr(self, modstr):
        try:
            p = re.compile("(.+) *\((.*)\)$")
            m = p.match(modstr.strip())
            rawname, rawresidues = m.group(1), m.group(2)
            name = rawname.strip()
            residues = list(rawresidues.replace(")", "").strip())
            return name, residues
        except Exception, e:
            raise Exception("Malformed modification string '%s'. Should be 'Name (Residues)'" % modstr)

    def _get_mass_from_unimod_or_string(self, key):
        entry = database.get_label(key)
        if entry:
            return float(entry['delta_mono_mass']), float(entry['delta_avge_mass'])
        else:
            # if its not a unimod entry try to parse masses from name itself
            try:
                mm, am = key.split("/")
                return float(mm), float(am)
            except:
                raise Exception(key + ": not found unimod and no valid mono/avg mass pair")

    def _modstr_to_list(self, modstr):
        modlist = []
        for mod in modstr.split(";"):
            # skip if empty ;;
            if not mod:
                continue
            name, residuearr = self._get_nameresiduelist_from_modstr(mod)
            mono, avg = self._get_mass_from_unimod_or_string(name)
            modlist.append([name, mono, avg, residuearr])
        return modlist


class XTandemModConverter(AbstractModConverter):
    def genmodstrs_to_engine(self, static_genmodstr, var_genmodstr):
        terminal_mods = ""
        smods = []
        for mod in self._modstr_to_list(static_genmodstr):
            name, mono, avg, residues = mod
            for residue in residues:
                smods.append("%f@%s" % (mono, residue))

        vmods = []
        for mod in self._modstr_to_list(var_genmodstr):
            name, mono, avg, residues = mod
            for residue in residues:
                #Peptide terminal modifications can be specified with the symbol '[' for N-terminus and ']' for C-terminus, such as 42.0@[ .
                if residue == "n":
                    residue = "["
                if residue == "c":
                    residue = "]"
                vmods.append("%f@%s" % (mono, residue))

        return ",".join(smods), ",".join(vmods), terminal_mods


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

    __tplNterm = """<MSModSpec>
    <MSModSpec_mod>
        <MSMod value="usermod$I">$NUM</MSMod>
    </MSModSpec_mod>
    <MSModSpec_type>
        <MSModType value="modnp">5</MSModType>
    </MSModSpec_type>
    <MSModSpec_name>$NAME</MSModSpec_name>
    <MSModSpec_monomass>$MONOMASS</MSModSpec_monomass>
        <MSModSpec_averagemass>$AVGMASS</MSModSpec_averagemass>
    <MSModSpec_n15mass>0</MSModSpec_n15mass>
    </MSModSpec>"""

    __tplCterm = """<MSModSpec>
    <MSModSpec_mod>
        <MSMod value="usermod$I">$NUM</MSMod>
    </MSModSpec_mod>
    <MSModSpec_type>
        <MSModType value="modcp">7</MSModType>
    </MSModSpec_type>
    <MSModSpec_name>$NAME</MSModSpec_name>
    <MSModSpec_monomass>$MONOMASS</MSModSpec_monomass>
        <MSModSpec_averagemass>$AVGMASS</MSModSpec_averagemass>
    <MSModSpec_n15mass>0</MSModSpec_n15mass>
    </MSModSpec>"""

    __tpltail = """</MSModSpecSet>"""

    def genmodstrs_to_engine(self, static_genmodstr, var_genmodstr):
        modtpl = self.__tplheader
        i = 0
        smods = []
        for mod in self._modstr_to_list(static_genmodstr):
            name, mono, avg, residues = mod
            for res in residues:
                i += 1
                if i > 9:
                    raise Exception("For Omssa only up to 10 modifications are suported")
                no = i + 118
                smods.append(str(no))
                dict_ = {"I": i, "NUM": no, "NAME": name, "MONOMASS": mono, "AVGMASS": avg, "RESIDUE": res}
                modtpl += Template(self.__tpl).safe_substitute(dict_)

        vmods = []
        for mod in self._modstr_to_list(var_genmodstr):
            name, mono, avg, residues = mod
            for res in residues:
                i += 1
                if i > 9:
                    raise Exception("For Omssa only up to 10 modifications are suported")
                no = i + 118
                vmods.append(str(no))
                dict_ = {"I": i, "NUM": no, "NAME": name, "MONOMASS": mono, "AVGMASS": avg, "RESIDUE": res}
                if res == "n":
                    tpl = self.__tplNterm
                elif res == "c":
                    tpl = self.__tplCterm
                else:
                    tpl = self.__tpl
                modtpl += Template(tpl).safe_substitute(dict_)

        modtpl += self.__tpltail
        return ",".join(smods), ",".join(vmods), modtpl


class MyrimatchModConverter(AbstractModConverter):
    def genmodstrs_to_engine(self, static_genmodstr, var_genmodstr):
        smods = []
        for mod in self._modstr_to_list(static_genmodstr):
            name, mono, avg, residues = mod
            for residue in residues:
                smods.append("%s %f" % (residue, mono))

        vmods = []
        for mod in self._modstr_to_list(var_genmodstr):
            name, mono, avg, residues = mod
            # special handling for n/c term modifications
            # variableModifications += nTerm + aminoAcidsAtTarget + cTerm + " " + symbols[symbolsCounter++] + " " + tempPtm.getMass() + " ";
            nTerm = ''
            cTerm = ''
            if 'n' in residues:
                residues.remove('n')
                nTerm = "("
            if 'c' in residues:
                residues.remove('c')
                cTerm = ")"
            middle = ""
            if residues:
                middle= "[%s]" % "".join(residues)
            vmods.append("%s%s%s * %f" % (nTerm,middle,cTerm, mono))

        return " ".join(smods), " ".join(vmods), None


class CometModConverter(AbstractModConverter):
    __fullnames = {"A": "alanine", "C": "cysteine", "D": "aspartic_acid", "E": "glutamic_acid", "F": "phenylalanine",
                   "G": "glycine", "H": "histidine", "I": "isoleucine", "K": "lysine", "L": "leucine",
                   "M": "methionine", "N": "asparagine", "O": "ornithine", "P": "proline", "Q": "glutamine",
                   "R": "arginine", "S": "serine", "T": "threonine", "V": "valine", "W": "tryptophan",
                   "Y": "tyrosine"}

    def genmodstrs_to_engine(self, static_genmodstr, var_genmodstr):
        smods = ""
        for mod in self._modstr_to_list(static_genmodstr):
            name, mono, avg, residues = mod
            for residue in residues:
                try:
                    smods += "add_%s_%s = %f\n" % (residue, self.__fullnames[residue], mono)
                except KeyError, e:
                    raise Exception("Residue " + e.message + " not known")

        vmods = ""
        i=0
        for mod in self._modstr_to_list(var_genmodstr):
            name, mono, avg, residues = mod
            if 'n' in residues:
                residues.remove('n')
                vmods += "variable_N_terminus = %s\n" % mono
            if 'c' in residues:
                residues.remove('c')
                vmods += "variable_C_terminus = %s\n" % mono
            if not residues: continue
            i+=1
            if i > 6: raise Exception("Comet only supports up to 6 variable mods")

            vmods += "variable_mod0%s = %f %s 0 3\n" % (i, mono, "".join(residues))


        return smods, vmods, None
