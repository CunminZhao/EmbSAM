import csv
import math

def find_string_in_csv(search_string, csv_file_path):
    formatted_search_string = "b'" + search_string + "'"
    positions = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row_index, row in enumerate(csv_reader):
            for column_index, cell in enumerate(row):
                if cell == formatted_search_string:
                    positions.append((row_index, column_index))
    return positions

def get_element_at_position(csv_content, row_index, column_index):
    if 0 <= row_index < len(csv_content) and 0 <= column_index < len(csv_content[row_index]):
        element = csv_content[row_index][column_index]
        if element.startswith("b'") and element.endswith("'"):
            return element[2:-1]
        else:
            return element
    else:
        return None 

def get_additional_element(csv_file_path, positions):
    if not positions:
        return None, None 
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_content = list(csv.reader(csvfile))

    adjacent_element = get_adjacent_element(csv_file_path, positions)
    row_index, column_index = positions[0]
    new_row_index = math.ceil(row_index / 2) 
    new_column_index = column_index - 1
    special_element = get_element_at_position(csv_content, new_row_index, new_column_index)

    return adjacent_element, special_element

def findname(cellname):
    if "AB" in cellname:
        return './confs/cell_name/name_AB.csv'
    elif 'C' in cellname:
        return './confs/cell_name/name_C.csv'
    elif 'D' in cellname:
        return './confs/cell_name/name_D.csv'
    elif 'E' in cellname:
        return './confs/cell_name/name_E.csv'
    elif 'MS' in cellname:
        return './confs/cell_name/name_MS.csv'
    elif 'P4' in cellname:
        return './confs/cell_name/name_P4.csv'
    else:
        return None
    
    
import csv

def find_string_in_csv(search_string, csv_file_path):
    formatted_search_string = "b'" + search_string + "'"
    positions = []
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row_index, row in enumerate(csv_reader):
            for column_index, cell in enumerate(row):
                if cell == formatted_search_string:
                    positions.append((row_index, column_index))
    return positions

def get_adjacent_element(csv_file_path, positions):
    if not positions:
        return None  

    
    row_index, column_index = positions[0]

    if row_index % 2 == 1:  
        new_row_index = row_index + 1
    else:  
        new_row_index = row_index - 1

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = list(csv.reader(csvfile))
        if 0 <= new_row_index < len(csv_reader):
            adjacent_element = csv_reader[new_row_index][column_index]
            if adjacent_element.startswith("b'") and adjacent_element.endswith("'"):
                return adjacent_element[2:-1]
            else:
                return adjacent_element
        else:
            return None
        

def binarytree(cellname):
    positions = find_string_in_csv(cellname, findname(cellname))
    daughter_cell, mother_cell = get_additional_element(findname(cellname), positions)
    if cellname=='MS':
        daughter_cell='E'
        mother_cell='EMS'
    if cellname=='E':
        daughter_cell='MS'
        mother_cell='EMS'
        
    if cellname=='C':
        daughter_cell='P3'
        mother_cell='P2'
    if cellname=='P3':
        daughter_cell='C'
        mother_cell='P2'
        
    if cellname=='D':
        daughter_cell='P4'
        mother_cell='P3'
    if cellname=='P4':
        daughter_cell='D'
        mother_cell='P3'
    
    if cellname=='EMS':
        daughter_cell='P2'
        mother_cell='P1'
    if cellname=='P2':
        daughter_cell='EMS'
        mother_cell='P1'
        
    if cellname=='ABa':
        daughter_cell='ABp'
        mother_cell='AB'
    if cellname=='ABp':
        daughter_cell='ABa'
        mother_cell='AB'
        
    return daughter_cell, mother_cell
