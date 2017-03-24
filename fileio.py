import ConfigParser
import re

class ProFileParser(object):
    def __init__(self, parent):

        self.parent = parent

    def read(self, filename):
        """Read project file"""
        
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
        file_list.reverse()  # reverse order (no copy)
        #file_list = file_list[::-1]  # copy and reverse order
        self.parent.caxfiles = file_list

        # segment node list
        nodes = re.split("\s+|,\s*", config.get("Bundle", "nodes"))
        nodes = filter(None, nodes)
        self.parent.nodes = map(int, nodes)
        if len(self.parent.nodes) != len(self.parent.caxfiles):
            print "Error: Invalid node list."
            return False

        # read content option
        self.parent.content = "filtered"  # default value
        if config.has_option("Bundle", "content"):
            self.parent.content = config.get("Bundle", "content")
        if self.parent.content not in ("filtered", "unfiltered"):
            print "Error: Unknown content option."
            return False

        # segment node list for BTF calc
        if config.has_section("BTF"):
            btf_nodes = re.split("\s+|,\s*", config.get("BTF", "nodes"))
            btf_nodes = filter(None, btf_nodes)
            self.parent.btf_nodes = map(int, btf_nodes)
        else:
            self.parent.btf_nodes = self.data.nodes

        return True

    def write(self, filename):
        pass
