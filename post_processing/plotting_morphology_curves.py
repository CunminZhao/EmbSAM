import os.path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# sns.set(font="Arial")


# embryo_name = 'Emb4'
# time_range=[57,92]
# gui_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\GUIData\{}'.format(
#     embryo_name)
#
# # =====================surface area curve================================
# surface_dataframe_plotting = pd.DataFrame(columns=['Cell Name', 'surface_area', 'time_point'])
# surface_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_surface.csv'.format(embryo_name)), index_col=0,
#                                 header=0).transpose()
#
# for index_this in surface_dataframe.index:
#
#     the_list_ = surface_dataframe.loc[index_this]
#     not_na_list = the_list_.notna().tolist()
#     this_cell_surface = the_list_[not_na_list]
#     for tp_this, surface_this in this_cell_surface.items():
#         # if surface_this < 4000:
#         if time_range[0]<=int(tp_this)<=time_range[1]:
#             surface_dataframe_plotting.loc[len(surface_dataframe_plotting)] = [str(index_this), float(surface_this),
#                                                                                (int(tp_this)-time_range[1]) * 10]
#
# ax = sns.lineplot(surface_dataframe_plotting, x='time_point', y='surface_area', hue='Cell Name')
#
# # sns.set(font="Arial")
#
# sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
#
# axis_font=28
# plt.xticks([-300,-200,-100,0],fontsize=axis_font,family='Arial')
# plt.yticks([1400,1600,1800,2000],fontsize=axis_font,family='Arial')
#
# plt.xlabel("Time (s)", size=28,family='Arial')
# plt.ylabel(r'Surface Area ($\rm \mu m^2$)', size=28,family='Arial')
#
# # plt.title('Post 4-cell Stage',size=24,family='Arial')
# plt.savefig(embryo_name+" surface area.pdf", format="pdf", dpi=300)
#
# plt.show()
# # ===============================================================================


embryo_name = 'Emb5'
time_range=[60,74]
# cell_name='ABpl'
cell_name='EMS'

# cell_name1='ABp'
# cell_name2='ABa'

# cel

gui_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\Public Data\ITK-SNAP-CVE Data\{}'.format(
    embryo_name)
# =====================contact area curve================================
contact_dataframe_plotting = pd.DataFrame(columns=['Cell-Cell Contact', 'contact_area', 'time_point'])
contact_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_Stat.csv'.format(embryo_name)), index_col=[0, 1],
                                header=0)

for index_this in contact_dataframe.index:
    # if True:
    if cell_name in index_this:
    # if cell_name1 in index_this or cell_name2 in index_this:
        the_list_ = contact_dataframe.loc[index_this]
        not_na_list = the_list_.notna().tolist()
        this_contact = the_list_[not_na_list]
        for tp_this, contact_this in this_contact.items():
            if time_range[0]<=int(tp_this)<=time_range[1] and contact_this>0:
                contact_dataframe_plotting.loc[len(contact_dataframe_plotting)] = [index_this[0]+'-'+index_this[1], float(contact_this)/2,
                                                                                   (int(tp_this)-time_range[1]) * 10]

ax = sns.lineplot(contact_dataframe_plotting, x='time_point', y='contact_area', hue='Cell-Cell Contact')

sns.set(font="Arial")

sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
font_size=28

plt.xticks([-150,-100,-50,0],fontsize=font_size,family='Arial')

# plt.xticks([-150,-100,-50,0],fontsize=font_size,family='Arial')

# plt.yticks([400, 450,500,550],fontsize=font_size,family='Arial') # AB
# plt.yticks([500,600,700,800],fontsize=font_size,family='Arial')
plt.yticks(fontsize=font_size,family='Arial')


plt.xlabel("Time (s)", size=font_size,family='Arial')
plt.ylabel(r'Contact Area ($\rm \mu m^2$)', size=font_size,family='Arial')

# plt.title('Post 4-cell Stage',size=24,family='Arial')
plt.savefig(embryo_name+" contact area "+".pdf", format="pdf", dpi=300)

plt.show()
# ================================================================================================================





# embryo_name = 'Emb5'
# time_range=[60,74]
# # cell_name='ABpl'
# cell_name='EMS'
#
# # cell_name1='ABa'
# # cell_name2='ABp'
#
# gui_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\Public Data\ITK-SNAP-CVE Data\{}'.format(
#     embryo_name)
# # =============================single cell surface area==========================
# surface_dataframe_plotting = pd.DataFrame(columns=['Cell', 'surface_area', 'time_point'])
# surface_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_surface.csv'.format(embryo_name)), index_col=0,
#                                 header=0).transpose()
#
# for index_this in surface_dataframe.index:
#     if index_this==cell_name:
#     # if index_this==cell_name1 or index_this==cell_name2:
#         the_list_ = surface_dataframe.loc[index_this]
#         not_na_list = the_list_.notna().tolist()
#         this_cell_surface = the_list_[not_na_list]
#         for tp_this, surface_this in this_cell_surface.items():
#             # if surface_this < 4000:
#             if time_range[0]<=int(tp_this)<=time_range[1]:
#                 surface_dataframe_plotting.loc[len(surface_dataframe_plotting)] = [str(index_this), float(surface_this),
#                                                                                    (int(tp_this)-time_range[1]) * 10]
#
# ax = sns.lineplot(surface_dataframe_plotting, x='time_point', y='surface_area',hue='Cell')
#
# sns.set(font="Arial")
#
# sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
#
#
# font_size=28
# plt.xticks([-150,-100,-50,0],fontsize=font_size,family='Arial') # ABA ABp
# plt.yticks(fontsize=font_size,family='Arial')
#
# plt.xlabel("Time (s)", size=font_size,family='Arial')
# plt.ylabel(r'Surface Area ($\rm \mu m^2$)', size=font_size,family='Arial')
#
# # plt.title('Post 4-cell Stage',size=24,family='Arial')
# plt.savefig(embryo_name+" surface area.pdf", format="pdf", dpi=300)
#
# plt.show()
# ==========================================================================================
