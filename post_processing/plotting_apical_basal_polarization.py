import os.path
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# ================================plotting curvessss===============================================
embryo_names = ['Emb4','Emb5']
tp_zero={'Emb4':92,'Emb5':34}
surface_dataframe_plotting = pd.DataFrame(
        columns=['Cell', 'Sample','surface_area', 'cell_cell_contact_area', 'polarization_ratio', 'time_point'])
# excluded_cells=[
#
#                 'MSp','ABalp','ABarp',
#
#                 'Ca','ABala','ABalpp','','ABplaa','ABplap','ABarpp','MSp'
#                 ]

for embryo_name in embryo_names:
    gui_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\Public Data\ITK-SNAP-CVE Data\{}'.format(
        embryo_name)

    # =====================contact area ================================
    contact_area_sum_dict = {}
    # contact_dataframe_plotting = pd.DataFrame(columns=['Cell-Cell Contact', 'contact_area', 'time_point'])
    contact_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_Stat.csv'.format(embryo_name)), index_col=[0, 1],
                                    header=0)

    for index_this in contact_dataframe.index:
        # if True:
        # if cell_name1 in index_this or cell_name2 in index_this:
        the_list_ = contact_dataframe.loc[index_this]
        not_na_list = the_list_.notna().tolist()
        this_contact = the_list_[not_na_list]
        for tp_this, contact_this in this_contact.items():
            cell1_tp = index_this[0] + '_' + tp_this
            cell2_tp = index_this[1] + '_' + tp_this
            if cell1_tp in contact_area_sum_dict.keys():
                contact_area_sum_dict[cell1_tp] += float(contact_this)
            else:
                contact_area_sum_dict[cell1_tp] = float(contact_this)

            if cell2_tp in contact_area_sum_dict.keys():
                contact_area_sum_dict[cell2_tp] += float(contact_this)
            else:
                contact_area_sum_dict[cell2_tp] = float(contact_this)

    # # =============================single cell surface area==========================

    surface_dataframe = pd.read_csv(os.path.join(gui_embryo_path, '{}_surface.csv'.format(embryo_name)), index_col=0,
                                    header=0).transpose()
    for index_this in surface_dataframe.index:
        # if str(index_this) not in excluded_cells:
        the_list_ = surface_dataframe.loc[index_this]
        not_na_list = the_list_.notna().tolist()
        this_cell_surface = the_list_[not_na_list]
        for tp_this, surface_this in this_cell_surface.items():
            inside_contact = contact_area_sum_dict.get(index_this + '_' + str(tp_this),0)
            if inside_contact>0:
                polarization_ratio = 1 - inside_contact / float(surface_this)
                surface_dataframe_plotting.loc[len(surface_dataframe_plotting)] = [str(index_this), embryo_name,float(surface_this),
                                                                                   inside_contact, polarization_ratio,
                                                                                   (tp_this-tp_zero[embryo_name])*10]
surface_dataframe_plotting.to_csv('Polarization plotting.csv')

surface_dataframe_plotting=pd.read_csv('Polarization plotting.csv')
# ax = sns.scatterplot(surface_dataframe_plotting,size=10, x='time_point', y='polarization_ratio', hue='Cell',style='Sample')
ax = sns.scatterplot(surface_dataframe_plotting,size=10, x='time_point', y='polarization_ratio', hue='Cell')

y_series=surface_dataframe_plotting['polarization_ratio'].tolist()
x_series=surface_dataframe_plotting['time_point'].tolist()
def objective(x, a, b):
    return a * x + b
popt, _ = curve_fit(objective, x_series, y_series)
# summarize the parameter values
a, b = popt
print('y = %.5f * x + %.5f' % (a, b))
correlation_coef=np.corrcoef(x_series,y_series)
print(correlation_coef)
x = np.linspace(min(x_series),max(x_series),1000)
y = a*x+b
plt.plot(x, y, '--', label='y=2x+1',c='black')
# matplotlib.rc('text', usetex = True)

font_size = 40

plt.text(-850, 0.3, 'R', fontsize = font_size, style='italic')
plt.text(-700, 0.3, ' = {}'.format(str(round(correlation_coef[0,1],4))), fontsize = font_size)

# matplotlib.rc('text', usetex = False)

sns.set(font="Arial")

sns.move_legend(ax, "upper left", ncol=2,bbox_to_anchor=(1, 1))

# plt.xticks([-150, -100, -50, 0], fontsize=font_size, family='Arial')  # ABA ABp
plt.xticks(fontsize=font_size, family='Arial')  # ABA ABp

plt.yticks(fontsize=font_size, family='Arial')

plt.xlabel("Developmental Time (s)", size=font_size, family='Arial')
plt.ylabel('Ratio of Outer Surface Area\nto Total Surface Area', size=font_size, family='Arial')

# plt.title('Post 4-cell Stage',size=24,family='Arial')
# plt.savefig(embryo_name + " Polarization Ratio.pdf", format="pdf", dpi=300)
figure = plt.gcf() # get current figure
figure.set_size_inches(18, 9)
# when saving, specify the DPI
# plt.savefig("myplot.png", dpi = 100)
plt.savefig("Polarization Ratio.pdf", format="pdf",dpi=100)


plt.show()
# ==========================================================================================


# =======================plotting morphology apical basal polarization==========================
