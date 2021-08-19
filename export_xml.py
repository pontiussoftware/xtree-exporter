import requests
import treelib
from treelib import Node, Tree
import sys
import pandas as pd
import xml.etree.ElementTree as ET

sys.setrecursionlimit(10 ** 5)

checked_leaves = []
nodes_not_added = []
# tree_dict = {}

credentials = pd.read_csv('/Users/cristinailli/Desktop/credentials.csv', sep=';')

### Parameters ###
api_username = credentials['api_username']
api_password = credentials['api_password']
vocabulary = 'http%3A%2F%2Fdigicult.vocnet.org%2Ftrachsler'
service = 'http://xtree-rest.digicult-verbund.de'
start = 'start'
count = 'count'
jsonfull = '0'
lang = 'all'
submit_action_getTopClassTC = 'getTopClassTC'
submit = 'Log+in'
submitID = '264859'
contributor_id = 'xtree-system'
url_prefix = 'http://xtree-rest.digicult-verbund.de/'
submit_Action_getFetchHierarchy = 'getFetchHierarchy'
request_url_getTopClassTC = url_prefix + submit_action_getTopClassTC + '?vocabulary=' + vocabulary + '&start=' + start + \
                            '&count=' + count + '&jsonfull=' + jsonfull + '&lang=' + lang + '&submit=' + submit_action_getTopClassTC

payload = {'userName': api_username, 'password': api_password, 'submit': submit, 'submitID': submitID}
url = 'http://xtree-rest.digicult-verbund.de/login.php'
xml_head = '<?xml version="1.0" encoding="UTF-8"?><Vocabulary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://vocabsservices.getty.edu/Schemas/AAT/AATGetSubject.xsd">'


# get lower level terms by ID
def getChildrenById(id):
    searchidslist = id
    # 'http://xtree-rest.digicult-verbund.de/getSearchVocItemsById?vocabulary=http%3A%2F%2Fdigicult.vocnet.org%2Ftrachsler
    #  &searchidslist=t00001&start=start&count=count&typeofvocitem=all&jsonfull=0&lang=all&submit=getSearchVocItemsById'
    typeofvocitem = 'all'
    submit_action_getSearchVocItemsById = 'getSearchVocItemsById'
    request_url_getSearchVocItemsById = 'http://xtree-rest.digicult-verbund.de/' + submit_action_getSearchVocItemsById \
                                        + '?vocabulary=' + vocabulary + '&searchidslist=' + searchidslist + '&start=' \
                                        + start + '&count=' + count + '&typeofvocitem=' + typeofvocitem + '&jsonfull=' \
                                        + jsonfull + '&lang=' + lang + '&submit=' + submit_action_getSearchVocItemsById

    # print('request_url_getSearchVocItemsById : ' + request_url_getSearchVocItemsById)
    getSearchVocItemsById_response = session.get(request_url_getSearchVocItemsById)
    dump_SearchVocItemsById = getSearchVocItemsById_response.json()
    dump_vocItemCount = dump_SearchVocItemsById['vocItemCount']
    dump_SearchVocItemsById_vocItems = dump_SearchVocItemsById['VocabularyItem']
    try:
        children = dump_SearchVocItemsById_vocItems[0]['Concept']['narrower']
        return children
    except:
        # print('ERROR NO CHILD for this node, it\'s a LEAF. Passing: ' + dump_SearchVocItemsById_vocItems[0]['Concept'][
        #     'id'])
        return dump_SearchVocItemsById_vocItems[0]['Concept']['id']


def getHierarchy():
    request_url_getFetchHierarchy = url_prefix + 'getFetchHierarchy?vocabulary=http%3A%2F%2Fdigicult.vocnet.org%2Ftrachsler&direction=down&level=N&start=1&count=3&typeofvocitem=all&term=Enter+single+term&jsonfull=0&lang=all&submit=getFetchHierarchy'
    print('URL : ' + request_url_getFetchHierarchy)
    getHierarchyResponse = session.get(request_url_getFetchHierarchy)
    dump_getHierarchyResponse = getHierarchyResponse.json()


def xml_topLevel_fields(Subject, concept, subject_ID):
    Hierarchy = Subject.makeelement('Hierarchy', {})
    Subject.append(Hierarchy)
    Hierarchy.text = concept['Term'][0]['Term']
    Sort_Order = Subject.makeelement('Sort_Order', {})
    Subject.append(Sort_Order)
    Sort_Order.text = '1'
    Terms = Subject.makeelement('Terms', {})
    Subject.append(Terms)
    Preferred_Term = Terms.makeelement('Preferred_Term', {})
    Terms.append(Preferred_Term)
    Term_Text = Preferred_Term.makeelement('Term_Text', {})
    Term_Text.text = concept['Term'][0]['Term']
    Preferred_Term.append(Term_Text)
    Term_ID = Preferred_Term.makeelement('Term_ID', {})
    Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Preferred_Term.makeelement('Term_Languages', {})
    Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][0]['lang']
    Term_Sources = Preferred_Term.makeelement('Term_Sources', {})
    Preferred_Term.append(Term_Sources)
    Source = Term_Sources.makeelement('Source', {})
    Term_Sources.append(Source)
    Source_ID = Source.makeelement('Source_ID', {})
    Source.append(Source_ID)
    Source_ID.text = 'Trachsler Schweiz'
    Source = Term_Sources.makeelement('Source', {})
    Term_Sources.append(Source)
    Source_ID = Source.makeelement('Source_ID', {})
    Source.append(Source_ID)
    Source_ID.text = 'http://digicult.vocnet.org/trachsler/' + subject_ID
    Preferred = Term_Sources.makeelement('Preferred', {})
    Term_Sources.append(Preferred)
    Non_Preferred_Term = Terms.makeelement('Non-Preferred_Term', {})
    Terms.append(Non_Preferred_Term)
    Term_Text = Non_Preferred_Term.makeelement('Term_Text', {})
    Non_Preferred_Term.append(Term_Text)
    Term_Text.text = concept['Term'][1]['Term']
    Term_ID = Non_Preferred_Term.makeelement('Term_ID', {})
    Non_Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Non_Preferred_Term.makeelement('Term_Languages', {})
    Non_Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][1]['lang']
    Non_Preferred_Term = Terms.makeelement('Non-Preferred_Term', {})
    Terms.append(Non_Preferred_Term)
    Term_Text = Non_Preferred_Term.makeelement('Term_Text', {})
    Non_Preferred_Term.append(Term_Text)
    Term_Text.text = concept['Term'][2]['Term']
    Term_ID = Non_Preferred_Term.makeelement('Term_ID', {})
    Non_Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Non_Preferred_Term.makeelement('Term_Languages', {})
    Non_Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][2]['lang']


def xml_child_fields(Subject, child_id, concept):
    Child = ET.SubElement(Subject, 'Subject', {'Subject_ID': child_id})
    Parent_Relationships = Child.makeelement('Parent_Relationships', {})
    Child.append(Parent_Relationships)
    Preferred_Parent = Parent_Relationships.makeelement('Preferred_Parent', {})
    Parent_Relationships.append(Preferred_Parent)
    Parent_Subject_ID = Preferred_Parent.makeelement('Parent_Subject_ID', {})
    Preferred_Parent.append(Parent_Subject_ID)
    Relationship_Type = Preferred_Parent.makeelement('Relationship_Type', {})
    Preferred_Parent.append(Relationship_Type)
    Relationship_Type.text = 'Parent/Child'
    Hierarchy = Child.makeelement('Hierarchy', {})
    Child.append(Hierarchy)
    Hierarchy.text = concept['Term'][0]['Term']
    Sort_Order = Child.makeelement('Sort_Order', {})
    Child.append(Sort_Order)
    Sort_Order.text = '1'
    Terms = Child.makeelement('Terms', {})
    Child.append(Terms)
    Preferred_Term = Terms.makeelement('Preferred_Term', {})
    Terms.append(Preferred_Term)
    Term_Text = Preferred_Term.makeelement('Term_Text', {})
    Term_Text.text = concept['Term'][0]['Term']
    Preferred_Term.append(Term_Text)
    Term_ID = Preferred_Term.makeelement('Term_ID', {})
    Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Preferred_Term.makeelement('Term_Languages', {})
    Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][0]['lang']
    Term_Sources = Preferred_Term.makeelement('Term_Sources', {})
    Preferred_Term.append(Term_Sources)
    Source = Term_Sources.makeelement('Source', {})
    Term_Sources.append(Source)
    Source_ID = Source.makeelement('Source_ID', {})
    Source.append(Source_ID)
    Source_ID.text = 'Trachsler Schweiz'
    Source = Term_Sources.makeelement('Source', {})
    Term_Sources.append(Source)
    Source_ID = Source.makeelement('Source_ID', {})
    Source.append(Source_ID)
    Source_ID.text = 'http://digicult.vocnet.org/trachsler/' + child_id
    Preferred = Term_Sources.makeelement('Preferred', {})
    Term_Sources.append(Preferred)
    Non_Preferred_Term = Terms.makeelement('Non-Preferred_Term', {})
    Terms.append(Non_Preferred_Term)
    Term_Text = Non_Preferred_Term.makeelement('Term_Text', {})
    Non_Preferred_Term.append(Term_Text)
    Term_Text.text = concept['Term'][1]['Term']
    Term_ID = Non_Preferred_Term.makeelement('Term_ID', {})
    Non_Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Non_Preferred_Term.makeelement('Term_Languages', {})
    Non_Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][1]['lang']
    Non_Preferred_Term = Terms.makeelement('Non-Preferred_Term', {})
    Terms.append(Non_Preferred_Term)
    Term_Text = Non_Preferred_Term.makeelement('Term_Text', {})
    Non_Preferred_Term.append(Term_Text)
    try:
        Term_Text.text = concept['Term'][2]['Term']
    except KeyError:
        print('reached a leaf')
    Term_ID = Non_Preferred_Term.makeelement('Term_ID', {})
    Non_Preferred_Term.append(Term_ID)
    Term_ID.text = concept['id']
    Term_Languages = Non_Preferred_Term.makeelement('Term_Languages', {})
    Non_Preferred_Term.append(Term_Languages)
    Term_Language = Term_Languages.makeelement('Term_Language', {})
    Term_Languages.append(Term_Language)
    Language = Term_Language.makeelement('Language', {})
    Term_Language.append(Language)
    Language.text = concept['Term'][2]['lang']
    # print('added: ' + child_id)


def add_children():
    global child
    leaves = helper_tree.leaves()
    leaves_id = []
    for leaf in leaves:
        leaves_id.append(leaf.tag)
    new_leaves = list(set(leaves_id) - set(checked_leaves))

    s = ET.tostring(root)
    for leaf_id in new_leaves:
        leaf_children = getChildrenById(leaf_id)
        if type(leaf_children) == str:
            checked_leaves.append(leaf_id)
        else:
            for child in leaf_children:
                leaf_child_id = child['Concept']['id']
                try:
                    helper_tree.create_node(leaf_child_id, leaf_child_id, parent=leaf_id)
                    # tree_dict.update({leaf_child_id: child['Concept']})
                    parent = root.find(".//Subject[@Subject_ID='" + leaf_id + "']")
                    xml_child_fields(parent, leaf_child_id, child['Concept'])
                except treelib.exceptions.DuplicatedNodeIdError:
                    nodes_not_added.append(leaf_child_id)
    # print('all leaves: ' + str(len(leaves)))
    # print('new leaves: ' + str(len(new_leaves)))
    # print('checked leaves: ' + str(len(checked_leaves)))
    if len(new_leaves) == 0:
        return
    else:
        add_children()


def create_tree():
    global subject_ID, child
    # cerate top level tree with its children
    for x in range(dump_vocItemCount):
        concept = dump_getTopClassTC_vocItems[x]['Concept']
        subject_ID = concept['id']
        if 'broader' not in concept:
            helper_tree.create_node(subject_ID, subject_ID, parent='root')
            # tree_dict.update({subject_ID: concept})
            Subject = ET.SubElement(root, 'Subject', {'Subject_ID': subject_ID})
            xml_topLevel_fields(Subject, concept, subject_ID)

            # adding data of children
            children_list = concept['narrower']
            for child in children_list:
                child_id = child['Concept']['id']
                # tree_dict.update({child_id: child['Concept']})
                helper_tree.create_node(child_id, child_id, parent=subject_ID)
                xml_child_fields(Subject, child_id, child['Concept'])
    add_children()
    if len(nodes_not_added) != 0:
        print('nodes not added:')
        print(nodes_not_added)


with requests.Session() as session:
    post = session.post(url, data=payload)
    getTopClassTC_response = session.get(request_url_getTopClassTC)
    # print('URL : ' + request_url_getTopClassTC)
    dump_getTopClassTC = getTopClassTC_response.json()
    dump_vocItemCount = dump_getTopClassTC['vocItemCount']
    dump_getTopClassTC_vocItems = dump_getTopClassTC['VocabularyItem']

    # root = ET.Element('root')
    root = ET.Element('Vocabulary', {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                     'xsi:noNamespaceSchemaLocation': 'http://vocabsservices.getty.edu/Schemas/AAT/AATGetSubject.xsd'})

    helper_tree = Tree()
    helper_tree.create_node('root', 'root')  # root node
    create_tree()

    # create a new XML file with the results
    xml_string = ET.tostring(root)
    file = open("export_xTree_trachsler.xml", "w")
    file.write('<?xml version="1.0" encoding="UTF-8"?>' + xml_string.decode('utf-8'))
    print('exported Trachsler to file')
