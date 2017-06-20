from pyqt_trace import pyqt_trace as qtrace

import ConfigParser
import re


class DefaultFileParser(object):
    def __init__(self, filename=None):
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(filename)
        
        split_str = self.config.get("WIN", "mainwin_size").split(",")
        self.mainwin_size = map(int, split_str)
        
        split_str = self.config.get("WIN", "mainwin_pos").split(",")
        self.mainwin_pos = map(int, split_str)

        split_str = self.config.get("WIN", "plotwin_size").split(",")
        self.plotwin_size = map(int, split_str)
        
        split_str = self.config.get("WIN", "plotwin_pos").split(",")
        self.plotwin_pos = map(int, split_str)

        self.background_color = self.config.get("FUE", "background_color")

        self.c4exe = self.config.get("C4", "cmd")
        self.libdir = self.config.get("C4", "libdir")
        self.default_version = self.config.get("C4", "default_version")
        self.default_neulib = self.config.get("C4", "default_neulib")
        self.default_gamlib = self.config.get("C4", "default_gamlib")
        self.grid_que = self.config.get("C4", "grid_que")



class InpFileParser(object):
    def __init__(self, parent):

        self.parent = parent

    def read(self, filename):
        """Read bundle input file"""
        
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read(filename):
                print "Could not open file '" + filename + "'"
                return False
        except:
            print "An error occured trying to read the file '" + filename + "'"
            return False

        # Get fuel type
        self.parent.fuetype = config.get("Bundle", "fuel")
        fuelist = ['A10XM', 'A10B', 'AT11', 'OPT2', 'OPT3']
        if self.parent.fuetype not in fuelist:
            print("Error: Unknown fuel type.")
            return False

        # cax files
        files = config.get("Bundle", "files")
        file_list = filter(None, re.split("\n", files))
        #file_list.reverse()  # reverse order (no copy)
        #file_list = file_list[::-1]  # copy and reverse order
        self.parent.caxfiles = file_list

        # segment node list
        nodes = re.split("\s+|,\s*", config.get("Bundle", "height"))
        nodes = filter(None, nodes)
        #nodes.reverse()
        #self.parent.nodes = map(int, nodes)
        self.parent.nodes = map(float, nodes)
        if len(self.parent.nodes) != len(self.parent.caxfiles):
            print "Error: Invalid node list."
            return False

        # height option
        #if config.has_option("Bundle", "height"):
        #    self.parent.height = config.get("Bundle", "height")
        #else:
        #    self.parent.height = "zone"

        ## read content option
        #self.parent.content = "filtered"  # default value
        #if config.has_option("Bundle", "content"):
        #    self.parent.content = config.get("Bundle", "content")
        #if self.parent.content not in ("filtered", "unfiltered"):
        #    print "Error: Unknown content option."
        #    return False

        # segment node list for BTF calc
        if config.has_section("BTF"):
            btf_nodes = re.split("\s+|,\s*", config.get("BTF", "height"))
            btf_nodes = filter(None, btf_nodes)
            #btf_nodes.reverse()
            #self.parent.btf_nodes = map(int, btf_nodes)
            self.parent.btf_nodes = map(float, btf_nodes)
        else:
            self.parent.btf_nodes = self.data.nodes

        return True

    def write(self, filename):
        """Save bundle data to file"""

        config = ConfigParser.SafeConfigParser()
        config.add_section("Bundle")
        config.set("Bundle", "fuel", self.parent.fuetype)

        # file_str = "\n".join(self.parent.caxfiles[::-1])  # save reverse order
        file_str = "\n".join(self.parent.caxfiles)
        config.set("Bundle", "files", file_str)

        # nodes = map(str, self.parent.nodes[::-1])
        height = map(str, self.parent.nodes)
        height_str = " ".join(height)
        config.set("Bundle", "height", height_str)

        #config.set("Bundle", "height", self.parent.height)

        config.add_section("BTF")
        # btf_nodes = map(str, self.parent.btf_nodes[::-1])
        btf_height = map(str, self.parent.btf_nodes)
        btf_str = " ".join(btf_height)
        config.set("BTF", "height", btf_str)
        
        with open(filename, "wb") as configfile:
            config.write(configfile)
