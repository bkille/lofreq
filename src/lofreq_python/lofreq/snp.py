#!/usr/bin/env python
"""Outdated, chromosome agnostic vcf alternative
"""



# Copyright (C) 2011, 2012 Genome Institute of Singapore
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

__author__ = "Andreas Wilm"
__email__ = "wilma@gis.a-star.edu.sg"
__copyright__ = "2011, 2012 Genome Institute of Singapore"
__license__ = "GPL2"


# --- standard library imports
#
import os
import sys

# --- third-party imports
#
# /

# --- project specific imports
#
# /


# --- globals
#
FIELDNAME_INFO = "Info"
# support for old field-names
FIELDNAME_STDDEV = "SD"
FIELDNAME_PVALUE = "P-Value"


    
class SNP(object):
    """
    A simple and generic SNP class.

    Original used http://www.hgvs.org/mutnomen/recs.html as template but than got rid of seqtype
    """

        
    def __init__(self, pos, wildtype, variant, chrom=None):
        """
        pos should be zero-offset
        """

        assert wildtype != variant        
        self.pos = pos
        self.wildtype = wildtype
        self.variant = variant
        self.chrom = chrom
        

    def __eq__(self, other):
        """
        if you define __eq__ you better implement __ne__ as well
        """

        if self.pos == other.pos and \
           self.wildtype == other.wildtype and \
           self.variant == other.variant and \
           self.chrom == other.chrom:
            return True
        else:
            return False


    def __ne__(self, other):
        """
        if you define __ne__ you better implement __eq__ as well
        """

        return not self.__eq__(other)

    

    def __str__(self):
        """
        http://stackoverflow.com/questions/1436703/difference-between-str-and-repr-in-python:
        The goal of __repr__ is to be unambiguous.
        The goal of __str__ is to be readable.
        """

        outstr = "%d %s>%s" % (self.pos+1, self.wildtype, self.variant)
        if self.chrom:
            outstr = "%s %s" % (self.chrom, outstr)
        return outstr


    def __hash__(self):
        """
        Needed for sets. FIXME why not just use __str__?
        """
        return hash("%s %d %s>%s" % (self.chrom, self.pos+1, self.wildtype, self.variant))




class ExtSNP(SNP):
    """
    Extended SNP representation used for the Dengue SNP caller
    project. Predictions can either come from the 'MFreq' method
    (having a frequency and a standard deviation) or from the 'MQual'
    method (having a frequency and a p-value). Allow arbitrary markup.
    Values will be stored as key=value;[key=value;...]. info should be
    a dictionary of key value pairs.

    NOTE: might be a good idea to associate arbitray data but would
    have to make sure that this is there for all SNPs then
    
    For comparison of two SNPs freq/stddev and pvalue will be ignored,
    ie only the basic SNP class comparison will be used.
    """
 
    def __init__(self, pos, wildtype, variant, freq, info=dict(), chrom=None):
        """
        pos should be zero offset
        """
 
        SNP.__init__(self, pos, wildtype, variant, chrom)

        self.freq = freq
        if info:
            assert isinstance(info, dict)
            for v in info:
                # used for constructing info string and therefore not
                # allowed to be in values
                assert ';' not in v
                assert ':' not in v
                

        self.info = info
            
        

    def __str__(self):
        """
        """

        #outstr = SNP.__str__(self)
        #if self.stddev:
        #    outstr = "%s %f" % (outstr, self.freq)
        #elif self.pvalue:
        #   outstr = "%s %f" % (outstr, self.pvalue)

        outstr = '%d %s>%s %g' % (self.pos+1,
                                  self.wildtype, self.variant,
                                  self.freq)
        if self.chrom:
            outstr = '%s %s' % (self.chrom, outstr)

        if self.info:
            info_str = ';'.join(["%s:%s"  % (k, v)
                                 for k, v in sorted(self.info.iteritems())])
            outstr = "%s %s" % (outstr, info_str)
            
        return outstr


    def __hash__(self):
        """
        Needed for sets. Don't just use str which includes extended info.
        SNPs with different freqs should still be the same
        """

        return SNP.__hash__(self)




    def identifier(self):
        """
        Returns an mappable identifier for this SNP, which is it's
        basic SNP class string representation (which does not contain
        freq, pvalue or stddev)
        """

        return SNP.__str__(self)


                
class DengueSNP(ExtSNP):
    """
    For backward compatibility when ExtSNP used to be called DengueSNP
    """
    
    def __init__(self, pos, wildtype, variant, freq,
                 stddev=None, pvalue=None):
        """
        Pos should be zero offset
        """

        ExtSNP.__init__(self, pos, wildtype, variant,
                        stddev=stddev, pvalue=pvalue)
            
    

def write_header(fh=sys.stdout, has_chrom=False):
    """
    """

    if has_chrom:
        fh.write("%s\n" % "Chrom Pos SNP Freq Info")
    else:
        fh.write("%s\n" % "Pos SNP Freq Info")
    
    
def write_record(snp_record, fh=sys.stdout):
    """write a single SNP to file
    """

    fh.write("%s\n" % snp_record)
    

def write_snp_file(fhandle, snp_list, has_chrom=False):
    """Writes SNP to a filehandle
    """
    
    #write_header(fhandle, has_chrom)        
    for snp in sorted(snp_list, key=lambda s: s.pos):
        write_record(snp, fhandle)

    

def parse_snp_file(filename, extra_fieldname='pvalue', has_header=False):
    """Parses a Dengue SNP file and returns parsed SNPs as list of
    ExtSNP instances. Missing wildtypes are allowed and replaced with N's.
    """

    ret_snp_list = []

    if filename == '-':
        fhandle = sys.stdin
    else:
        fhandle = open(filename, 'r')

    for line in fhandle:
        line = line.rstrip(os.linesep)
        if len(line)==0 or line.startswith("#") or line.startswith("Pos") or line.startswith("Chrom"):
            continue
        line_split = line.split()
        if len(line_split) == 5:
            (chrom, pos, snp_str, freq, info_str) = line_split
        elif len(line_split) == 4:
            chrom = None
            (pos, snp_str, freq, info_str) = line_split
        else:
            raise ValueError, (
                "Failed to parse line from %s. Line was '%s'" % (filename, line))

        pos = int(pos)-1
        freq = float(freq)
        
        # old versions don't contain the wildtype. use 'N' instead.
        if ">" in snp_str:
            (wildtype, variant) = snp_str.split(">")
        else:
            wildtype = 'N'
            variant = snp_str

        try:
            info = dict([e.split(':') for e in info_str.split(';')])
        except ValueError:
            info = {"generic-info": info_str}
        new_snp = ExtSNP(pos, wildtype, variant, freq, info, chrom)
        ret_snp_list.append(new_snp)

    if fhandle != sys.stdin:
        fhandle.close()
    return ret_snp_list



def test(fsnp_in=None, fsnp_out=None):
    """
    a test function
    """

    snp = SNP(111, 'C', 'T')
    print "Got SNP: %s" % snp
    
    snp = SNP(666, 'G', 'A', 'r')
    print "Got SNP: %s" % snp

    info = {'pvalue': 0.025}
    dengue_snp = ExtSNP(12345, 'A', 'U', 2e-4, info)
    print "Got Dengue SNP: %s" % dengue_snp

    if fsnp_in:
        print "Parsing %s" % fsnp_in
        snps = parse_snp_file(fsnp_in)
        for snp in snps:
            print "Parsed SNP: %s" % snp
        if fsnp_out:
            print "Writing to %s" % fsnp_out
            write_snp_file(fsnp_out, snps)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    