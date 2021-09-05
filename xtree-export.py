import requests
import treelib
import argparse
import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET
from treelib import Node, Tree

# Constants
url_prefix = 'https://xtree-rest.digicult-verbund.de/'
url_getSearchVocItemsById = url_prefix + 'getSearchVocItemsById'
url_getTopClassTC = url_prefix + 'getTopClassTC'
url_getFetchHierarchy = url_prefix + 'getFetchHierarchy'

sys.setrecursionlimit(10 ** 5)

checked_leaves = []
nodes_not_added = []
# tree_dict = {}

# Parse program arguments
parser = argparse.ArgumentParser(description="Program arguments for XTree exporter.")
parser.add_argument('-v', '--vocabulary', dest='vocabulary', help='The vocabulary to download.')
parser.add_argument('-u', '--username', dest='username', help='Username to use for authentication with XTree.')
parser.add_argument('-p', '--password', dest='password', help='Password to use for authentication with XTree.')
parser.add_argument('-o', '--output', dest='output', help='The path to the resulting output files.')
parser.add_argument('-n', '--name', dest='name', help='Name of the output file.')
arguments = parser.parse_args()

### Parameters ###
api_username = arguments.username
api_password = arguments.password
vocabulary = arguments.vocabulary  # Trachsler: http://digicult.vocnet.org/trachsler

# Prepare empty CSV data
csv_data = {
    'id': [],
    'notation': [],
    'de': [],
    'fr': [],
    'it': []
}


# get lower level terms by ID
def getChildrenById(id):
    respone = session.get(url_getSearchVocItemsById,
                          params={'vocabulary': vocabulary, 'searchidslist': id, 'start': 'start',
                                  'count': 'count', 'jsonfull': 0, 'lang': 'all', 'typeofvocitem': 'all'})
    if respone.status_code != 200:
        print('Failed to load top child terms (vocabulary=' + arguments.vocabulary + ",id=" + id + ')')
        exit(1)

    try:
        return respone.json()['VocabularyItem'][0]['Concept']['narrower']
    except:
        return None


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
        if leaf_children is None:
            checked_leaves.append(leaf_id)
        else:
            for child in leaf_children:
                leaf_child_id = child['Concept']['id']
                try:
                    helper_tree.create_node(leaf_child_id, leaf_child_id, parent=leaf_id)
                    parent = root.find(".//Subject[@Subject_ID='" + leaf_id + "']")

                    try:
                        normalized = child['Concept']['Term'][0]['Term']
                        child['Concept']['Term'][0]['Term'] = normalized
                    except KeyError:
                        print('Concept ' + child['Concept']['id'] + ' does not have a DE term.')
                        child['Concept']['Term'][0]['Term'] = ''

                    try:
                        normalized = child['Concept']['Term'][1]['Term']
                        child['Concept']['Term'][1]['Term'] = normalized
                    except KeyError:
                        print('Concept ' + child['Concept']['id'] + ' does not have a FR term.')
                        child['Concept']['Term'][1]['Term'] = ''

                    try:
                        normalized = child['Concept']['Term'][2]['Term']
                        child['Concept']['Term'][2]['Term'] = normalized
                    except KeyError:
                        print('Concept ' + child['Concept']['id'] + ' does not have a IT term.')
                        child['Concept']['Term'][2]['Term'] = ''

                    xml_child_fields(parent, leaf_child_id, child['Concept'])
                    add_to_csv_frame(child['Concept'])
                except treelib.exceptions.DuplicatedNodeIdError:
                    nodes_not_added.append(leaf_child_id)
    if len(new_leaves) == 0:
        return
    else:
        add_children()


def add_to_csv_frame(concept):
    csv_data['id'].append(concept['id'])
    csv_data['notation'].append(concept['notation'])
    csv_data['de'].append(concept['Term'][0]['Term'])
    csv_data['fr'].append(concept['Term'][1]['Term'])
    csv_data['it'].append(concept['Term'][2]['Term'])


def create_tree():
    # Create top level tree with its children
    global subject_ID, child
    for x in range(vocItemCount):
        concept = vocItems[x]['Concept']
        subject_ID = concept['id']
        if 'broader' not in concept:
            helper_tree.create_node(subject_ID, subject_ID, parent='root')
            # tree_dict.update({subject_ID: concept})
            Subject = ET.SubElement(root, 'Subject', {'Subject_ID': subject_ID})
            xml_topLevel_fields(Subject, concept, subject_ID)
            add_to_csv_frame(concept)

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
    # 1: Attempt login
    login_response = session.post('http://xtree-rest.digicult-verbund.de/login.php',
                                  data={'userName': api_username, 'password': api_password, 'submit': 'Log+In',
                                        'submitID': 264859})
    if login_response.status_code != 200:
        print('Login to XTree failed. Please check your credentials')
        exit(1)

    # 2: Load top level items of selected vocabulary
    response = session.get(url_getTopClassTC,
                           params={'vocabulary': vocabulary, 'start': 'start', 'count': 'count',
                                   'jsonfull': 0, 'lang': 'all'})
    if response.status_code != 200:
        print('Failed to load top level terms for vocabulary: ' + arguments.vocabulary)
        exit(1)

    # Extract necessary data
    dump = response.json()
    vocItemCount = dump['vocItemCount']
    vocItems = dump['VocabularyItem']

    # Prepare XML root
    root = ET.Element('Vocabulary', {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                     'xsi:noNamespaceSchemaLocation': 'http://vocabsservices.getty.edu/Schemas/AAT/AATGetSubject.xsd'})
    # Start to build-up tree.
    helper_tree = Tree()
    helper_tree.create_node('root', 'root')  # root node
    create_tree()

    # Create a new XML file with the results
    with open(os.path.join(arguments.output, arguments.name + '.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write(ET.tostring(root, encoding='unicode'))
        print('Successfully exported vocabulary to XML-file.')

    # Create a new tabulator separated file with the results
    with open(os.path.join(arguments.output, arguments.name + '.txt'), 'w', encoding='utf-8') as f:
        pd.DataFrame(csv_data).sort_values('notation').to_csv(f, sep='\t', index=False, encoding='utf-8')
        print('Successfully exported vocabulary to CSV-file.')

    print('Done!')
