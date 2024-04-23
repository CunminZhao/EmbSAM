import os
import io

# from termcolor import colored
import pandas as pd
from treelib import Tree, Node


def read_cd_file(cd_file_path):
    """
    csv file!
    :param cd_file_path:
    :return:
    """
    df_nuc_tmp = pd.read_csv(cd_file_path)
    df_nuc = df_nuc_tmp[['cell', 'time', 'x', 'y', 'z']]
    df_nuc = df_nuc.astype({"x": float, "y": float, "z": float, "time": int})
    return df_nuc

def construct_celltree(nucleus_file_path, max_time, name_dict_path):
    '''
    Construct cell tree structure with cell names
    :param nucleus_file_path:  the name list file to the tree initilization
    :param max_time: the maximum time point to be considered
    :return cell_tree: cell tree structure where each time corresponds to one cell (with specific name)
    '''
    ## Get cell number

    # pd_number = pd.read_csv(name_dict_path, names=["name", "label"])
    label_name_dict = pd.read_csv(name_dict_path, index_col=0).to_dict()['0']
    name_label_dict = {value: key for key, value in label_name_dict.items()}
    # name_label_dict = pd.Series(pd_number.label.values, index=pd_number.name).to_dict()

    ##  Construct cell
    #  Add unregulized naming
    cell_tree = Tree()
    # cell_node_this = cell_node()
    # cell_node_this.set_number(name_label_dict['P0'])
    cell_tree.create_node('P0', 'P0')
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['AB'])
    cell_tree.create_node('AB', 'AB', parent='P0',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['P1'])
    cell_tree.create_node('P1', 'P1', parent='P0',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['EMS'])
    cell_tree.create_node('EMS', 'EMS', parent='P1',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['P2'])
    cell_tree.create_node('P2', 'P2', parent='P1',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['P3'])
    cell_tree.create_node('P3', 'P3', parent='P2',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['C'])
    cell_tree.create_node('C', 'C', parent='P2',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['P4'])
    cell_tree.create_node('P4', 'P4', parent='P3',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['D'])
    cell_tree.create_node('D', 'D', parent='P3',data=cell_node_this)

    # cell_node_this = cell_node()
    # cell_node_this.set_number(name_label_dict['Z2'])
    # cell_tree.create_node('Z2', 'Z2', parent='P4',data=cell_node_this)
    # cell_node_this = cell_node()
    # cell_node_this.set_number(name_label_dict['Z3'])
    # cell_tree.create_node('Z3', 'Z3', parent='P4',data=cell_node_this)

    # EMS
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['E'])
    cell_tree.create_node('E', 'E', parent='EMS',data=cell_node_this)
    cell_node_this = cell_node()
    cell_node_this.set_number(name_label_dict['MS'])
    cell_tree.create_node('MS', 'MS', parent='EMS',data=cell_node_this)

    # Read the name excel and construct the tree with complete segCell
    df_time = read_cd_file(nucleus_file_path)

    # read and combine all names from different acetrees

    # =====================================
    # dynamic update the name dictionary
    # =====================================
    # cell_in_dictionary = list(name_label_dict.keys())
    #
    # ace_pd = df_time[df_time.time <= max_time]
    # cell_list = list(ace_pd.cell.unique())
    # add_cell_list = list(set(cell_list) - set(cell_in_dictionary))
    #
    # if len(add_cell_list) != 0:
    #     assert len(add_cell_list) == 0, "Name dictionary should be updated"
    #     # print(colored("Name dictionary updated", "red"))
    #     # ================================= cancel dynamic updating ============
    #     # add_cell_list.sort()
    #     # print("Name dictionary updated !!!")
    #     # add_number_dictionary = dict(zip(add_cell_list, range(len(cell_in_dictionary) + 1, len(cell_in_dictionary) + len(add_cell_list) + 1)))
    #     # number_dictionary.update(add_number_dictionary)
    #     # pd_number_dictionary = pd.DataFrame.from_dict(number_dictionary, orient="index")
    #     # pd_number_dictionary.to_csv('./dataset/number_dictionary.csv', header=False)

    df_time = df_time[df_time.time <= max_time]
    all_cell_names = list(df_time.cell.unique()) # get all cell name
    # print(all_cell_names)
    for cell_name in list(all_cell_names):
        if cell_name not in name_label_dict.keys():
            continue
        times = list(df_time.time[df_time.cell==cell_name])
        cell_node_this = cell_node()
        cell_node_this.set_number(name_label_dict[cell_name])
        cell_node_this.set_time(times)
        if not cell_tree.contains(cell_name):
            if "Nuc" not in cell_name:
                parent_name = cell_name[:-1]
                cell_tree.create_node(cell_name, cell_name, parent=parent_name, data=cell_node_this)
        else:
            cell_tree.update_node(cell_name, data=cell_node_this)

    return cell_tree


class cell_node(object):
    # Node Data in cell tree
    def __init__(self):
        self.number = 0
        self.time = 0

    def set_number(self, number):
        self.number = number

    def get_number(self):

        return self.number

    def set_time(self, time):
        self.time = time

    def get_time(self):

        return self.time