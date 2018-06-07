from lxml import etree
from collections import defaultdict


class YangXmlDiff :
    
    def __init__(self, verify_callback=None, print_callback=None, verbose = 3):
        self.verify_callback=verify_callback
        self.print_callback=print_callback
        self.verbose = verbose
        
    def default_print(self, msg):
        #print nothing for verbose = 0        
        if self.verbose is 0:
            return
        #print only errors if verbose = 3
        elif self.verbose is 3:
            if 'ERR:' not in msg:
               return
        if self.print_callback is None:
            print(msg)
        else:
            self.print_callback(msg)
    
    def compare_root(self, expected, actual):
        '''
        DESCRIPTION: compare element from root
        INPUT: expected- type of 'xml.etree.ElementTree.ElementTree'
               actual - type of 'xml.etree.ElementTree.ElementTree '
        OUTPUT: return True is tree matches, otherwise False
        '''
        
        expected_list = list(expected.getroot())
        actual_list = list(actual.getroot())
        return self.compare_children(expected_list, actual_list, True)

    def process_list(self, expected, actual):
 
        expected_ordered = []
        
        for ch_actual in actual:
            found = False
            found_idx = -1
            for idx, ch_expected in enumerate(expected):
                if self.compare_children_wrapper(ch_expected, ch_actual, False) is True:
                    expected_ordered.append(ch_expected)
                    found = True
                    found_idx = idx
                    self.default_print ("INFO:found matching element {a} {b}".format(a=idx, b=ch_expected.text))
                    break
            if found is True:
                del expected[found_idx]
            if found is False:
                self.default_print ("ERR:incorrect list instance {a}".format(a=ch_actual))
                return False
        if len(actual) == len(expected_ordered):
            for ch1,ch2 in zip(expected_ordered, actual):
                ret = self.compare_children_wrapper(ch1, ch2, True)
                if ret is False:
                    self.default_print ("ERR:list instance {a} and {b} does not match".format(a=ch1, b=ch2))
                    return ret
        else :
            diff = [i for i,j in zip(expected_ch_keys, actual_ch_keys) if i != j]
            self.default_print ("ERR:list instances are not same {a}".format(a=diff))
     
        return True
        

    def compare_children_wrapper(self, expected, actual, is_recursive = False):
        '''
        DESCRIPTION: compare element from root
        INPUT: expected- type of 'xml.etree.ElementTree.Element'
               actual - type of 'xml.etree.ElementTree.Element'
        OUTPUT: return True is tree matches, otherwise False
        '''
        #compare nodes here first
        if self.verify_callback is None:
            self.verify_callback = self.compare_leafs
            
        expected_ch_list = list(expected)
        actual_ch_list = list(actual)
        return self.compare_children(expected_ch_list, actual_ch_list, is_recursive)
    
    #default callback for comparing leafs
    def compare_leafs(self, expected_node, actual_node):
        #pdb.set_trace()
        if expected_node is None or actual_node is None:
            return False
        expected_tag = expected_node.tag.strip()
        actual_tag   = actual_node.tag.strip()
        
        if (expected_tag != actual_tag):
            self.default_print ("ERR:nodes {a} does not match: value {b}".format(a=actual_tag, b= expected_tag))
            return False
        
        # if both none return true
        if expected_node.text is None and actual_node.text is None:
            return True
        #if only one None, then return mismatch False
        if expected_node.text is None or actual_node.text is None:
            return False
        expected_text = expected_node.text.strip()
        actual_text   = actual_node.text.strip()

        if (expected_text != actual_text):
            self.default_print ("ERR:node {a} does not match value{b} : value {c}".format(a=actual_tag, b=expected_text, c=actual_text))
            return False
        else:
            return True
  
    def compare_children(self, expected_ch_list, actual_ch_list, is_recursive = False):
       
        
        if self.verify_callback is None:
            self.verify_callback = self.compare_leafs
            
       
        if len(expected_ch_list) != len(actual_ch_list):
            self.default_print ("ERR:Mismatch in number of childrens")
            self.default_print ("ERR:expected {a}".format(a=expected_ch_list))
            self.default_print ("ERR:actual {a}".format(a=actual_ch_list))
            return False
        else:
            self.default_print ("INFO:same number of childrens {a}".format(a=len(actual_ch_list)))
        
        expected_ch_dict = defaultdict(list)
        actual_ch_dict = defaultdict(list)
        
        for ch1 in expected_ch_list:
            expected_ch_dict[ch1.tag].append(ch1)
            
        for ch2 in actual_ch_list:
            actual_ch_dict[ch2.tag].append(ch2)
  
            
        expected_ch_keys = expected_ch_dict.keys()
        actual_ch_keys = actual_ch_dict.keys()
                  
        diff = [i for i,j in zip(expected_ch_keys, actual_ch_keys) if i != j]
        
        if len(diff) > 0 :
            self.default_print ("ERR:keys does not match {}".format(diff))
            return False
            
        #compare leafs
        leafs_list = []
        container_list = []
        for key, value in actual_ch_dict.items():
            if (len(value) == 1):
                if self.verify_callback(expected_ch_dict[key][0], value[0]) is True:
                    if len(list(expected_ch_dict[key][0])) == 0 and len(actual_ch_dict[key][0]) == 0:
                        leafs_list.append(key)
                else:
                    return False
        self.default_print("INFO:leaf list {a}".format(a=leafs_list))
        
        #delete all leafs:
        for l in leafs_list:
            del expected_ch_dict[l]
            del actual_ch_dict[l]
         
        if is_recursive is True:
            for key, value in expected_ch_dict.items():
                ret = True
                if (len(value) == 1):
                    ret = self.compare_children_wrapper(value.pop(), actual_ch_dict[key].pop(), True)
                else :
                    ret = self.process_list(value, actual_ch_dict[key])
                if ret is False:
                    return ret
        return True;
