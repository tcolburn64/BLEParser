# Imports
import tkinter
from tkinter import *
from tkinter import ttk
import datetime
from tkinter.ttk import Treeview
import os.path

from matplotlib.figure import Figure

import DB_Utils
import Utility_Code
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt

# Global Variables

utility_code = Utility_Code


# lines = []

# Form Methods


def get_file_name():

    try:
        status("Select file...")
        print(source_file_path.get())
        source_file_path.set(filedialog.askopenfilename(filetypes=[("Ellisys Raw Packet Import Format", "*.bttrp")]))
        print(source_file_path.get())
        status("Source File Selected. Getting Data File...")
        x = 0
        while os.path.exists(source_file_path.get() + "_" + str(x) + ".db"):
            x += 1
        data_file_path.set(source_file_path.get() + "_" + str(x) + ".db")
        print("Source and data files set.")
        # items = get_lines(_file.get())
    except ValueError:
        pass


def parse_file_name():
    status("Parsing File...")
    _advertisers = utility_code.get_lines(source_file_path.get(), data_file_path.get(), pb, mainframe)
    status("Parse complete.")
    advertiser_count=0
    for advertiser in _advertisers:
        advertiser_count += 1
        if (advertiser_count % 2 == 0):
            advertisers.insert("", "end", text="1", values=(advertiser.address, int(advertiser.first_time_stamp)/1000000000, int(advertiser.last_time_stamp)/1000000000, advertiser.item_count, str((int(advertiser.last_time_stamp)-int(advertiser.first_time_stamp))/1000000000), str(((int(advertiser.last_time_stamp)-int(advertiser.first_time_stamp))/int(advertiser.item_count))/1000000000)), tags=('evenrow',))
        else:
            advertisers.insert("", "end", text="1", values=(advertiser.address, int(advertiser.first_time_stamp)/1000000000, int(advertiser.last_time_stamp)/1000000000, advertiser.item_count, str((int(advertiser.last_time_stamp)-int(advertiser.first_time_stamp))/1000000000), str(((int(advertiser.last_time_stamp)-int(advertiser.first_time_stamp))/int(advertiser.item_count))/1000000000)), tags=('oddrow',))

    pb['value'] = 0
    mainframe.update()

def status(stat_string):
    status_string.set(stat_string)
    mainframe.update()


def tree_clear_all(treename):
    for item in treename.get_children():
        treename.delete(item)


def tree_fill(treename, tree_data):
    row_count = 0
    for tree_datum in tree_data:
        row_count += 1
        if (row_count % 2 == 0):
            treename.insert("", "end", text="1", values=(tree_datum.central_address, tree_datum.peripheral_address, int(tree_datum.connect_ind_timestamp)/1000000000, int(tree_datum.first_data_packet_timestamp)/1000000000, int(tree_datum.last_data_timestamp)/1000000000, (int(tree_datum.last_data_timestamp) - int(tree_datum.first_data_packet_timestamp))/1000000000), tags=('evenrow',))
        else:
            treename.insert("", "end", text="1", values=(tree_datum.central_address, tree_datum.peripheral_address, int(tree_datum.connect_ind_timestamp)/1000000000, int(tree_datum.first_data_packet_timestamp)/1000000000, int(tree_datum.last_data_timestamp)/1000000000, (int(tree_datum.last_data_timestamp) - int(tree_datum.first_data_packet_timestamp))/1000000000), tags=('oddrow',))



def tree_clear_and_fill(treename, treedata):
    tree_clear_all(treename)
    tree_fill(treename, treedata)


# UX Root
root = Tk()
root.title("Ellisys export parsing summary")
root.geometry("1400x800")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky="W, E, N, S")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.rowconfigure(4, weight=1)


# UX Variables
source_file_path = StringVar()
data_file_path = StringVar()
status_string = StringVar()


# UX Objects
get_file_button: Button = ttk.Button(mainframe, text="Select File", command=get_file_name)
get_file_button.grid(column=0, row=0, sticky=W)

ttk.Label(mainframe, textvariable=source_file_path).grid(column=1, row=0, sticky=W)
ttk.Label(mainframe, textvariable=data_file_path).grid(column=1, row=1, sticky=W)

# mainframe.update()
# print(file_path.get())
parse_file_button: Button = ttk.Button(mainframe, text="Parse File", command=parse_file_name)
parse_file_button.grid(column=0, row=1, sticky=W)

ttk.Label(mainframe, textvariable=status_string).grid(column=0, row=2, sticky=W)
# get_file_button.invoke()
advertisers: Treeview = ttk.Treeview(mainframe, columns=("0", "1", "2", "3", "4", "5"), show="headings", height=750)
advertisers.grid(column=0, row=4, columnspan=6, sticky=tkinter.NW, rowspan=2)
advertisers.column(column=0, anchor=W, minwidth=0, width=120, stretch=NO)
advertisers.heading(column=0, text="Advertiser")
advertisers.column(column=1, anchor=W, minwidth=0, width=80, stretch=NO)
advertisers.heading(column=1, text="First_Time_Stamp")
advertisers.column(column=2, anchor=W, minwidth=0, width=80, stretch=NO)
advertisers.heading(column=2, text="Last_Time_Stamp")
advertisers.column(column=3, anchor=W, minwidth=0, width=80, stretch=NO)
advertisers.heading(column=3, text="Adv_Count")
advertisers.column(column=4, anchor=W, minwidth=0, width=80, stretch=NO)
advertisers.heading(column=4, text="Total_Time")
advertisers.column(column=5, anchor=W, minwidth=0, width=120, stretch=NO)
advertisers.heading(column=5, text="Average_Interval")

connection_tree: Treeview = ttk.Treeview(mainframe, columns=("0", "1", "2", "3", "4", "5"), show="headings", height=750)
connection_tree.grid(column=6, row=4, columnspan=6, sticky=tkinter.NW, rowspan=2)
connection_tree.column(column=0, anchor=W, minwidth=0, width=120, stretch=NO)
connection_tree.heading(column=0, text="Central")
connection_tree.column(column=1, anchor=W, minwidth=0, width=80, stretch=NO)
connection_tree.heading(column=1, text="Peripheral")
connection_tree.column(column=2, anchor=W, minwidth=0, width=80, stretch=NO)
connection_tree.heading(column=2, text="Connect_timestamp")
connection_tree.column(column=3, anchor=W, minwidth=0, width=80, stretch=NO)
connection_tree.heading(column=3, text="First_data_packet")
connection_tree.column(column=4, anchor=W, minwidth=0, width=80, stretch=NO)
connection_tree.heading(column=4, text="Last_Data_packet")
connection_tree.column(column=5, anchor=W, minwidth=0, width=120, stretch=NO)
connection_tree.heading(column=5, text="Timespan")

# mainframe.update()
# get_lines_button = ttk.Button(mainframe, text="Start parse", command=Utility_Code.get_lines(file))
# get_lines_button.grid(column=0, row=1, sticky=W)
# lines = get_lines_button.invoke()
# items = parse_lines(lines)
# mainframe.update()
pb = ttk.Progressbar(mainframe, orient='horizontal', mode='determinate', length=560)
pb.grid(column=0, row=5, columnspan=6, padx=10, pady=20, sticky=W)
# ttk.Label(mainframe, textvariable=file).grid(column=1, row=0, sticky=W)
style = ttk.Style()
style.theme_use("default")

style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=25, fieldbackground="#D3D3D3")
style.map("Treeview", background=[('selected', 'blue')])
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
# folder_button.focus()
# root.bind("<Return>", get_folder_name())


# Create striped row tags
advertisers.tag_configure('oddrow', background="white")
advertisers.tag_configure('evenrow', background="lightblue")

connection_tree.tag_configure('oddrow', background="white")
connection_tree.tag_configure('evenrow', background="lightblue")

# Create Binding Function


def display_advertiser_timing_graph(event):
    advertiser = advertisers.selection()
    item_details = advertisers.item(advertiser)
    advertiser_address = item_details.get("values")[0]
    resultsxy = utility_code.get_advertiser_timing_data(data_file_path.get(), advertiser_address)
    connections = utility_code.find_connections(data_file_path.get(), advertiser_address)
    tree_clear_and_fill(connection_tree, connections)
    mainframe.update()
    # xmax = 0
    # xmin = 1000000000000
    # ymax = 0
    # ymin = 1000000000000
    # for result in results:
    #     xmax = max(xmax, result[0])
    #     xmin = min(xmin, result[0])
    #     ymax = max(ymax, result[1])
    #     ymin = min(ymin, result[1])



    # outlier_low_count = 0
    # outlier_low_first = 1000000000000
    # outlier_low_last = 0
    # sixty_ms_adv_count = 0
    # sixty_ms_adv_first = 1000000000000
    # sixty_ms_adv_last = 0
    # outlier_med_count = 0
    # outlier_med_first = 1000000000000
    # outlier_med_last = 0
    # twoeleven_ms_adv_count = 0
    # twoeleven_ms_adv_first = 1000000000000
    # twoeleven_ms_adv_last = 0
    # outlier_high_count = 0
    # outlier_high_first = 1000000000000
    # outlier_high_last = 0
    #
    #
    # for result in results:
    #     if result[4] < 60000000:
    #         outlier_low_count+=1
    #         outlier_low_first = min(result[3], outlier_low_first)
    #         outlier_low_last = max(result[3], outlier_low_last)
    #     elif result[4] >= 60000000 and result[4] <= 70000000:
    #         sixty_ms_adv_count+=1
    #         sixty_ms_adv_first = min(result[3], sixty_ms_adv_first)
    #         sixty_ms_adv_last = max(result[3], sixty_ms_adv_last)
    #     elif result[4] > 70000000 and result[4] < 211250000:
    #         outlier_med_count += 1
    #         outlier_med_first = min(result[3], outlier_med_first)
    #         outlier_med_last = max(result[3], outlier_med_last)
    #     elif result[4] >= 211250000 and result[4] <= 221250000:
    #         twoeleven_ms_adv_count += 1
    #         twoeleven_ms_adv_first = min(result[3], twoeleven_ms_adv_first)
    #         twoeleven_ms_adv_last = max(result[3], twoeleven_ms_adv_last)
    #     elif result[4] > 221250000:
    #         outlier_high_count += 1
    #         outlier_high_first = min(result[3], outlier_high_first)
    #         outlier_high_last = max(result[3], outlier_high_last)
    #
    # print("low=" + str(outlier_low_count) + " : " + str(outlier_low_first/1000000000) + " : " + str(outlier_low_last/1000000000) + " : " + str((outlier_low_last-outlier_low_first)/1000000000))
    # print("sixty=" + str(sixty_ms_adv_count) + " : " + str(sixty_ms_adv_first/1000000000) + " : " + str(sixty_ms_adv_last/1000000000) + " : " + str((sixty_ms_adv_last-sixty_ms_adv_first)/1000000000))
    # print("med=" + str(outlier_med_count) + " : " + str(outlier_med_first/1000000000) + " : " + str(outlier_med_last/1000000000) + " : " + str((outlier_med_last-outlier_med_first)/1000000000))
    # print("twoeleven=" + str(twoeleven_ms_adv_count) + " : " + str(twoeleven_ms_adv_first/1000000000) + " : " + str(twoeleven_ms_adv_last/1000000000) + " : " + str((twoeleven_ms_adv_last-twoeleven_ms_adv_first)/1000000000))
    # print("high=" + str(outlier_high_count) + " : " + str(outlier_high_first/1000000000) + " : " + str(outlier_high_last/1000000000) + " : " + str((outlier_high_last-outlier_high_first)/1000000000))
    # fig = Figure()
    # ax = fig.add_axes()
#    cx = fig.add_subplot()
#    ax.plot(resultsx, resultsy)
    if len(resultsxy)>0:
        fig, ax = plt.subplots()
        fig.suptitle(advertiser_address)
        x, y = zip(*resultsxy)
        ax.plot(x, y)
        ax.set(xlabel='time', ylabel='Advertising Interval', title='Advertising Interval')
        ax.grid()
    #    cx = plt.subplots()
        # ax.plot(results[3], results[4], linewidth=2.0)
        # ax.set()
        # ax.show()
        # hp = np.random.normal(200000,25000, 5000)

        # plt.plot(True, True, results)
        # plt.hist2d(results[0], results[1])
        plt.show()



# Bindings
advertisers.bind("<ButtonRelease-1>", display_advertiser_timing_graph)



status("Mainloop")
root.mainloop()
