
from yang_xml import YangXmlDiff as xmldiff
import xml.etree.ElementTree as ET
import unittest

expected = ET.parse('test_xml/expected.txt')
actual = ET.parse('test_xml/actual.txt')

def my_node_compare(expected_node, actual_node):
    '''
    DOCSTRING: custom xml comparison function if there is extra attribute
    skip in the attributes.
    INPUT: expected_node- expected node as ElementTree, 
           actual_node- actual node is ElementTree
    OUTPUT: returns True is matches, otherwise False
    '''
    #pdb.set_trace()
    if expected_node is None or actual_node is None:
        return False
    expected_tag = expected_node.tag.strip()
    actual_tag   = actual_node.tag.strip()
   
    # if both none return true
    if expected_node.text is None and actual_node.text is None:
        return True
    #if only one None, then return mismatch False
    if expected_node.text is None or actual_node.text is None:
        print ("leaf {a} or  {b} is empty".format(a=actual_tag, b=expected_tag))
        return False
    
    expected_text = expected_node.text.strip()
    actual_text   = actual_node.text.strip()

    if 'skip' in expected_node.attrib.keys():
        if expected_node.attrib['skip'].lower() == 'true':
            return True
    elif (expected_text != actual_text):
        print ("leaf {a} does not match value{b} : value {c}".format(a=actual_tag, b=expected_text, c=actual_text))
        return False
    else:
        return True

class TestXml_diff(unittest.TestCase):
   
    
    def test_one_positive(self):
        yangXmlDiff = xmldiff.YangXmlDiff(my_node_compare, verbose=1)
        result = yangXmlDiff.compare_root(expected, actual)
        self.assertEqual(result, True)
    def test_one_positive_empty_type(self):
        expected = ET.parse('test_xml/expected_1.txt')
        actual = ET.parse('test_xml/actual_1.txt')
        yangXmlDiff = xmldiff.YangXmlDiff(my_node_compare, verbose=1)
        result = yangXmlDiff.compare_root(expected, actual)
        self.assertEqual(result, True)

if __name__ == "__main__":
    unittest.main()


