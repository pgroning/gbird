import ConfigParser
import re

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
        nodes = re.split("\s+|,\s*", config.get("Bundle", "nodes"))
        nodes = filter(None, nodes)
        #nodes.reverse()
        #self.parent.nodes = map(int, nodes)
        self.parent.nodes = map(float, nodes)
        if len(self.parent.nodes) != len(self.parent.caxfiles):
            print "Error: Invalid node list."
            return False

        ## read content option
        #self.parent.content = "filtered"  # default value
        #if config.has_option("Bundle", "content"):
        #    self.parent.content = config.get("Bundle", "content")
        #if self.parent.content not in ("filtered", "unfiltered"):
        #    print "Error: Unknown content option."
        #    return False

        # segment node list for BTF calc
        if config.has_section("BTF"):
            btf_nodes = re.split("\s+|,\s*", config.get("BTF", "nodes"))
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
        nodes = map(str, self.parent.nodes)
        node_str = "\n".join(nodes)
        config.set("Bundle", "nodes", node_str)

        #config.set("Bundle", "content", self.parent.content)

        config.add_section("BTF")
        # btf_nodes = map(str, self.parent.btf_nodes[::-1])
        btf_nodes = map(str, self.parent.btf_nodes)
        btf_str = "\n".join(btf_nodes)
        config.set("BTF", "nodes", btf_str)
        
        with open(filename, "wb") as configfile:
            config.write(configfile)
