import os.path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

embryo_name = 'Emb4'
gui_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\GUIData\{}'.format(
    embryo_name)

# =====================surface area curve================================
# surface_dataframe_plotting = pd.DataFrame(columns=['cell_name', 'surface_area', 'time_point'])
# surface_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_surface.csv'.format(embryo_name)), index_col=0,
#                                 header=0).transpose()
#
# for index_this in surface_dataframe.index:
#     the_list_ = surface_dataframe.loc[index_this]
#     not_na_list = the_list_.notna().tolist()
#     this_cell_surface = the_list_[not_na_list]
#     for tp_this, surface_this in this_cell_surface.items():
#         # if surface_this < 4000:
#         surface_dataframe_plotting.loc[len(surface_dataframe_plotting)] = [str(index_this), float(surface_this),
#                                                                            int(tp_this) * 10]
#
# ax = sns.lineplot(surface_dataframe_plotting, x='time_point', y='surface_area', hue='cell_name')
#
# # ax.legend(loc='upper left',, title="Title")
#
# sns.move_legend(ax, "upper left", ncol=2, bbox_to_anchor=(1, 1))
#
# plt.xticks([1, 500, 1000, 1500, 2000, 2500], fontsize=16)
#
# plt.yticks(fontsize=16)
#
# plt.xlabel("Time (Second)", size=20)
# plt.ylabel(r'Surface Area ($\mu m^2$)', size=20)
# # plt.savefig(embryo_name+" surface are.pdf", format="pdf", dpi=300)
#
# plt.show()
# ===============================================================================

# =====================contact area curve================================
contact_dataframe_plotting = pd.DataFrame(columns=['cell_pairs', 'contact_area', 'time_point'])
contact_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_Stat.csv'.format(embryo_name)), index_col=[0, 1],
                                header=0)

for index_this in contact_dataframe.index:
    the_list_ = contact_dataframe.loc[index_this]
    not_na_list = the_list_.notna().tolist()
    this_contact = the_list_[not_na_list]
    for tp_this, contact_this in this_contact.items():
        if contact_this > 10:
            contact_dataframe_plotting.loc[len(contact_dataframe_plotting)] = [str(index_this), float(contact_this),
                                                                               int(tp_this) * 10]

ax = sns.lineplot(contact_dataframe_plotting, x='time_point', y='contact_area', hue='cell_pairs')

# ax.legend(loc='upper left',, title="Title")

sns.move_legend(ax, "upper left", ncol=2, bbox_to_anchor=(1, 1))

plt.xticks([1, 500, 1000, 1500, 2000, 2500], fontsize=16)

plt.yticks(fontsize=16)

plt.xlabel("Time (Second)", size=20)
plt.ylabel(r'Contact Area ($\mu m^2$)', size=20)
# plt.savefig(embryo_name+" surface are.pdf", format="pdf", dpi=300)

plt.show()