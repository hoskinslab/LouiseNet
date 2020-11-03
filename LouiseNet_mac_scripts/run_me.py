# GUI modules
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import CustomTkinterWidgets as ctk
import tkinter.ttk as ttk
import sys

# Other Modules
from PIL import ImageTk, Image
from LouiseNet_backend import *
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import platform

# --Global Variables--
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)  # Change the current working directory to the base path
dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
icon_path = dir_path+'/img/icon.ico'
logo_path = dir_path+'/img/logo.png'


def open_image(path: str, size: tuple = None, keep_aspect: bool = True, rotate: int = 0) -> ImageTk.PhotoImage:
    """
    Open the image on the path and apply given settings\n
    Paramaters:
        path(str):
            Absolute path of the image
        size(tuple):
            first value - width
            second value - height
        keep_aspect(bool):
            keep aspect ratio of image and resize
            to maximum possible width and height
            (maxima are given by size)
        rotate(int):
            clockwise rotation of image
    Returns(ImageTk.PhotoImage):
        Image of path
    """
    img = Image.open(path).convert(mode='RGBA')
    ratio = img.height/img.width
    img = img.rotate(angle=-rotate)
    if size is not None:
        size = (int(size[0]), int(size[1]))
        if keep_aspect:
            img = img.resize((size[0], int(size[0] * ratio)), Image.ANTIALIAS)
        else:
            img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)


class MainWindow(tk.Tk):
    # --Constants--
    PRI_BG_COLOR = '#78aaff'
    SEC_BG_COLOR = '#CADEFF'
    COLOR_2 = '#accbff'

    # --Layout--
    UPLOAD_BUTTON = {'x': 10, 'y': 10, 'width': -20, 'height': -20,
                     'relx': 0, 'rely': 0, 'relwidth': 1, 'relheight': 0.35}
    UPLOAD_LABEL = {'x': 10, 'y': 0, 'width': -20, 'height': -10,
                    'relx': 0, 'rely': 0.35, 'relwidth': 1, 'relheight': 0.65}

    def __init__(self):
        # Run the __init__ method on the tk.Tk class
        super().__init__()

        # --Window Settings--
        self.title("LOUISENET")
        # Disable resizing of window for both axes
        # self.resizable(False, False)
        win_width = 900
        win_height = 475
        # Set Geometry and Center Window
        self.geometry('{width}x{height}+{xpad}+{ypad}'.format(
            width=win_width,
            height=win_height,
            xpad=int(self.winfo_screenwidth()/2 -
                     win_width/2),
            ypad=int(self.winfo_screenheight()/2 -
                     win_height/2)))
        # Set background color to white
        self.configure(bg=self.PRI_BG_COLOR)
        # ctk.create_style()
        self.update()

        # --Variables--
        self.icon_img = open_image(path=icon_path,)
        self.logo_img = open_image(path=logo_path, size=(200, 100))
        # -Tkinter Value Holders-
        # Radiobutton values
        self.interaction_var = tk.StringVar(value='main')
        self.edgeList_var = tk.StringVar(value='letter')
        # File paths
        self.pdbFilePath_var = tk.StringVar(value='')
        self.csvFilePath_var = tk.StringVar(value='')
        self.chrFilePath_var = tk.StringVar(value='')
        # Protein Info
        self.proteinName_var = tk.StringVar(value='')
        self.wantedProteinId_var = tk.StringVar(value='')
        self.layout_type = tk.StringVar(value='circular')

        # --Widgets--
        self.create_widgets()
        self.configure_widgets()
        self.place_widgets()

        # --Other Options--
        self.iconphoto(True, self.icon_img)  # Set icon image
        self.update()

    # -Widget Methods-
    def create_widgets(self):
        """Create window widgets"""
        # -Frames-
        self.options_Frame = tk.Frame(self)
        self.fill_options_Frame()
        self.upload_Frame = tk.Frame(self)
        self.fill_upload_Frame()
        self.protein_Frame = tk.Frame(self)
        self.fill_protein_Frame()
        # -Logo-
        self.logo_Label = tk.Label(self, compound='center', background=self.PRI_BG_COLOR,
                                   image=self.logo_img, anchor=tk.CENTER)
        self.logo_Label.image = self.logo_img
        # -Buttons-
        if platform.system() == 'Darwin':
            self.run_Button = tk.Button(self, text='Select Directory & Run',
                                        font=17, highlightbackground=self.PRI_BG_COLOR,
                                        command=self.run)
            self.analysis_Button = tk.Button(self, text='Network Analysis',
                                             font=13, highlightbackground=self.PRI_BG_COLOR,
                                             command=self.network_analysis)
            self.plot_Button = tk.Button(self, text='Plot Network',
                                         font=13, highlightbackground=self.PRI_BG_COLOR,
                                         command=self.plot_network)
        else:
            self.run_Button = ctk.Button(self, text='Select Directory & Run',
                                         font=17, command=self.run)
            self.analysis_Button = ctk.Button(self, text='Network Analysis',
                                              font=13, command=self.network_analysis)
            self.plot_Button = ctk.Button(self, text='Plot Network',
                                          font=13, command=self.plot_network)
        OptionList = ['', 'circular', 'kamada_kawai',
                      'random', 'spectral', 'spring', 'shell']
        if platform.system() == 'Darwin':
            self.plot_options = tk.OptionMenu(
                self, self.layout_type, *OptionList)
            self.plot_options.configure(
                background=self.PRI_BG_COLOR,
                highlightbackground=self.PRI_BG_COLOR,
                highlightcolor=self.PRI_BG_COLOR,
            )
            self.update_idletasks()
            self.update()
        else:
            self.plot_options = ttk.OptionMenu(
                self, self.layout_type, *OptionList)

    def configure_widgets(self):
        """Change widget styling and appearance"""

        # -Frames-
        MAIN_FRAME_CON = {'background': '#ececec' if platform.system() == 'Darwin' else self.SEC_BG_COLOR,
                          'highlightbackground': '#628BD1',
                          'highlightthickness': 1
                          }
        PATH_FRAME_CON = {'background': '#FFFFFF',
                          'highlightcolor': self.COLOR_2,
                          'highlightbackground': self.COLOR_2,
                          'highlightthickness': 2
                          }
        self.options_Frame.configure(**MAIN_FRAME_CON)
        self.upload_Frame.configure(**MAIN_FRAME_CON)
        self.protein_Frame.configure(**MAIN_FRAME_CON)
        # File Uploading
        self.upload_csv_Frame.configure(**PATH_FRAME_CON)
        self.upload_chr_Frame.configure(**PATH_FRAME_CON)
        self.upload_pdb_Frame.configure(**PATH_FRAME_CON)

        # -Labels-
        ttk.Style().configure('Title.TLabel',
                              background=self.COLOR_2,
                              foreground='#000')
        ttk.Style().configure('Path.TLabel',
                              background='#F6F6F6',
                              foreground='#666',
                              )
        ttk.Style().configure('Protein.TLabel',
                              background=self.SEC_BG_COLOR,
                              foreground='#333',
                              anchor=tk.W)
        self.options_interaction_Label.configure(background=self.SEC_BG_COLOR,
                                                 foreground='#000')

        # -Buttons-
        ttk.Style().configure('TButton',
                              background=self.PRI_BG_COLOR,
                              highlightbackground=self.PRI_BG_COLOR
                              )
        ttk.Style().configure('Path.TButton',
                              background='#FFF',)
        # -Radiobuttons-
        ttk.Style().configure('Interaction.TRadiobutton',
                              background=self.SEC_BG_COLOR)

        # -Optionmenu-
        ttk.Style().configure(self.plot_options.winfo_class(),
                              highlightbackground=self.PRI_BG_COLOR)

    def place_widgets(self):
        """Place main widgets"""
        # -Frames-
        self.options_Frame.place(x=20, y=20, width=-40, height=-20,
                                 relx=0, rely=0, relwidth=1, relheight=0.25)
        self.upload_Frame.place(x=20, y=10, width=-30, height=-10,
                                relx=0, rely=0.25, relwidth=0.75, relheight=0.5)
        self.protein_Frame.place(x=0, y=10, width=-20, height=-10,
                                 relx=0.75, rely=0.25, relwidth=0.25, relheight=0.5)
        # -Logo-
        self.logo_Label.place(x=20, y=0, width=-20, height=0,
                              relx=0, rely=0.75, relwidth=0.45, relheight=0.25)
        # -Buttons-
        self.run_Button.place(x=30, y=10 + 5, width=-80, height=-15,
                              relx=0.45, rely=0.75, relwidth=0.55, relheight=0.25/2)
        self.analysis_Button.place(x=10, y=0 + 5, width=-60, height=-20,
                                   relx=0.75, rely=0.75 + 0.25/2, relwidth=0.25, relheight=0.25/2)

        self.plot_Button.place(x=30, y=0 + 5, width=-30, height=-20,
                               relx=0.45, rely=0.75 + 0.25/2, relwidth=0.2, relheight=0.25/2)
        self.plot_options.place(x=0, y=0 + 7, width=0, height=-24,
                                relx=0.65, rely=0.75 + 0.25/2, relwidth=0.10, relheight=0.25/2)
        # if platform.system() == 'Darwin':  # MacOS
        # else:
        #     self.plot_Button.place(x=30, y=0 + 5, width=-48, height=-20,
        #                            relx=0.4, rely=0.75 + 0.25/2, relwidth=0.25, relheight=0.25/2)
        #     self.plot_options.place(x=27, y=0 + 7, width=-32, height=-24,
        #                             relx=0.69, rely=0.75 + 0.25/2, relwidth=0.25/3.8, relheight=0.25/2)
        self.update_idletasks()
        self.update()

    # Filling Methods
    def fill_options_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        # Title
        self.options_title_Label = ctk.Label(self.options_Frame,
                                             text='Options', font=20,
                                             style='Title.TLabel')
        # Interaction
        self.options_interaction_Label = ctk.Label(self.options_Frame,
                                                   text='Select Network Type', font=12,)
        self.options_main_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                        text='Chains Only', font=11,
                                                        variable=self.interaction_var, value='main',
                                                        style='Interaction.TRadiobutton')
        self.options_detailed_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                            text='Chains & Residues', font=11,
                                                            variable=self.interaction_var, value='detail',
                                                            style='Interaction.TRadiobutton')
        # Edge List
        self.options_edgeList_Label = ctk.Label(self.options_Frame,
                                                text='Select Edgelist Output', font=12,)
        self.options_letter_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                          text='Chain ID', font=11,
                                                          variable=self.edgeList_var, value='letter',
                                                          style='EdgeList.TRadiobutton')
        self.options_name_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                        text='Chain Name', font=11,
                                                        variable=self.edgeList_var, value='name',
                                                        style='EdgeList.TRadiobutton')
        self.options_number_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                          text='Network ID', font=11,
                                                          variable=self.edgeList_var, value='number',
                                                          style='EdgeList.TRadiobutton')
        # plot network
        self.options_n_plot_Label = ctk.Label(self.options_Frame,
                                              text='Select Network Layout', font=12,)
        self.options_letter_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                          text='Chain ID', font=11,
                                                          variable=self.edgeList_var, value='letter',
                                                          style='EdgeList.TRadiobutton')
        self.options_name_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                        text='Chain Name', font=11,
                                                        variable=self.edgeList_var, value='name',
                                                        style='EdgeList.TRadiobutton')
        self.options_number_Radiobutton = ctk.Radiobutton(self.options_Frame,
                                                          text='Node ID', font=11,
                                                          variable=self.edgeList_var, value='number',
                                                          style='EdgeList.TRadiobutton')
        # -Place Widgets-
        # Title
        self.options_title_Label.place(x=0, y=0, width=0, height=0,
                                       relx=0, rely=0, relwidth=0.25, relheight=1)
        # Interaction
        self.options_interaction_Label.place(x=0, y=0, width=0, height=0,
                                             relx=0.25, rely=0, relwidth=0.3, relheight=0.5)
        self.options_main_Radiobutton.place(x=0, y=0, width=0, height=0,
                                            relx=0.6, rely=0, relwidth=0.2, relheight=0.5)
        self.options_detailed_Radiobutton.place(x=0, y=0, width=0, height=0,
                                                relx=0.8, rely=0, relwidth=0.2, relheight=0.5)
        # Edge List
        self.options_edgeList_Label.place(x=0, y=0, width=0, height=0,
                                          relx=0.25, rely=0.5, relwidth=0.3, relheight=0.5)
        self.options_letter_Radiobutton.place(x=0, y=0, width=0, height=0,
                                              relx=0.55, rely=0.5, relwidth=0.45/3, relheight=0.5)
        self.options_name_Radiobutton.place(x=0, y=0, width=0, height=0,
                                            relx=0.55 + 0.45/3, rely=0.5, relwidth=0.45/3, relheight=0.5)
        self.options_number_Radiobutton.place(x=0, y=0, width=0, height=0,
                                              relx=1 - 0.45/3, rely=0.5, relwidth=0.45/3, relheight=0.5)

    def fill_upload_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        # Title
        self.upload_title_Label = ctk.Label(self.upload_Frame,
                                            text='Upload Files', font=20,
                                            style='Title.TLabel')
        # Frames
        self.upload_pdb_Frame = tk.Frame(self.upload_Frame)
        self.fill_upload_pdb_Frame()
        self.upload_csv_Frame = tk.Frame(self.upload_Frame)
        self.fill_upload_csv_Frame()
        self.upload_chr_Frame = tk.Frame(self.upload_Frame)
        self.fill_upload_chr_Frame()
        # -Place Widgets-
        # Title
        self.upload_title_Label.place(x=0, y=0, width=0, height=0,
                                      relx=0, rely=0, relwidth=1, relheight=0.25)
        # Frames
        self.upload_pdb_Frame.place(x=0, y=0, width=0, height=0,
                                    relx=0/3, rely=0.25, relwidth=1/3, relheight=0.75)
        self.upload_csv_Frame.place(x=0, y=0, width=0, height=0,
                                    relx=1/3, rely=0.25, relwidth=1/3, relheight=0.75)
        self.upload_chr_Frame.place(x=0, y=0, width=0, height=0,
                                    relx=2/3, rely=0.25, relwidth=1/3, relheight=0.75)

    def fill_upload_pdb_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        if platform.system() == 'Darwin':
            self.upload_pdb_upload_Button = tk.Button(self.upload_pdb_Frame,
                                                      text='Select Structure File',
                                                      command=self.open_pdb_filedialog,
                                                      highlightbackground='#FFF'
                                                      )
        else:
            self.upload_pdb_upload_Button = ctk.Button(self.upload_pdb_Frame,
                                                       text='Select Structure File',
                                                       command=self.open_pdb_filedialog,
                                                       style='Path.TButton',
                                                       )

        self.upload_pdb_path_Label = ctk.Label(self.upload_pdb_Frame,
                                               textvariable=self.pdbFilePath_var,
                                               style='Path.TLabel', font=9)
        # Bind geometry change of this widget to updating the wraplength
        self.upload_pdb_path_Label.bind('<Configure>', self.update_wraplengths)

        # -Place Widgets-
        self.upload_pdb_upload_Button.place(**self.UPLOAD_BUTTON)
        self.upload_pdb_path_Label.place(**self.UPLOAD_LABEL)

    def fill_upload_csv_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        if platform.system() == 'Darwin':
            self.upload_csv_upload_Button = tk.Button(self.upload_csv_Frame,
                                                      text='Select Mapping File',
                                                      command=self.open_csv_filedialog,
                                                      highlightbackground='#FFF'
                                                      )
        else:
            self.upload_csv_upload_Button = ctk.Button(self.upload_csv_Frame,
                                                       text='Select Mapping File',
                                                       command=self.open_csv_filedialog,
                                                       style='Path.TButton',
                                                       )
        self.upload_csv_path_Label = ctk.Label(self.upload_csv_Frame,
                                               textvariable=self.csvFilePath_var,
                                               style='Path.TLabel', font=9)
        # -Place Widgets-
        self.upload_csv_upload_Button.place(**self.UPLOAD_BUTTON)
        self.upload_csv_path_Label.place(**self.UPLOAD_LABEL)

    def fill_upload_chr_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        if platform.system() == 'Darwin':
            self.upload_chr_upload_Button = tk.Button(self.upload_chr_Frame,
                                                      text='Select Chrome Driver',
                                                      command=self.open_chr_filedialog,
                                                      highlightbackground='#FFF'
                                                      )
        else:
            self.upload_chr_upload_Button = ctk.Button(self.upload_chr_Frame,
                                                       text='Select Chrome Driver',
                                                       command=self.open_chr_filedialog,
                                                       style='Path.TButton',
                                                       )
        self.upload_chr_path_Label = ctk.Label(self.upload_chr_Frame,
                                               textvariable=self.chrFilePath_var,
                                               style='Path.TLabel', font=9)
        # -Place Widgets-
        self.upload_chr_upload_Button.place(**self.UPLOAD_BUTTON)
        self.upload_chr_path_Label.place(**self.UPLOAD_LABEL)

    def fill_protein_Frame(self):
        """Fill Frame with neccessary widgets"""
        # -Create Widgets-
        # Title
        self.protein_title_Label = ctk.Label(self.protein_Frame,
                                             text='Structure Info', font=20,
                                             style='Title.TLabel')
        # Protein Name
        self.protein_name_Label = ctk.Label(self.protein_Frame,
                                            text='Output File Name', font=10,
                                            style='Protein.TLabel')
        self.protein_name_Entry = ctk.Entry(self.protein_Frame,
                                            textvariable=self.proteinName_var, font=13,
                                            justify=tk.CENTER)
        # Protein ID
        self.protein_id_Label = ctk.Label(self.protein_Frame,
                                          text='Chain ID of Residues', font=10,
                                          style='Protein.TLabel')
        self.protein_id_Entry = ctk.Entry(self.protein_Frame,
                                          textvariable=self.wantedProteinId_var, font=13,
                                          justify=tk.CENTER)
        # -Place Widgets-
        # Title
        self.protein_title_Label.place(x=0, y=0, width=0, height=0,
                                       relx=0, rely=0, relwidth=1, relheight=0.25)
        # Protein Name
        self.protein_name_Label.place(x=20, y=-5, width=-40, height=0,
                                      relx=0, rely=0.35, relwidth=1, relheight=0.1)
        self.protein_name_Entry.place(x=20, y=-5, width=-40, height=0,
                                      relx=0, rely=0.45, relwidth=1, relheight=0.15)
        # Protein ID
        self.protein_id_Label.place(x=20, y=-5, width=-40, height=0,
                                    relx=0, rely=0.65, relwidth=1, relheight=0.1)
        self.protein_id_Entry.place(x=20, y=-5, width=-40, height=0,
                                    relx=0, rely=0.75, relwidth=1, relheight=0.15)

    # -Filedialogs-
    def open_pdb_filedialog(self):
        """
        Open a filedialog to select a pdb file
        """
        path = tk.filedialog.askopenfilename(
            parent=self,
            title=f'Select Structure File',
            initialfile='',
            filetypes=[
                ('Structure File', '.pdb .cif')
            ])
        if path:  # Path selected
            if not path.lower().endswith(('.pdb', '.cif')):
                tk.messagebox.showerror(master=self,
                                        title='Invalid File',
                                        message='Please select a ".pdb" or a ".cif" file!',  # nopep8
                                        detail=f'File: {path}')
                return
            self.pdbFilePath_var.set(path)

    def open_csv_filedialog(self):
        """
        Open a filedialog to select a csv file
        """
        path = tk.filedialog.askopenfilename(
            parent=self,
            title=f'Select CSV File',
            initialfile='',
            filetypes=[
                ('CSV File', '.csv'),
            ])
        if path:  # Path selected
            if not path.lower().endswith('.csv'):
                tk.messagebox.showerror(master=self,
                                        title='Invalid File',
                                        message='Please select a ".csv" file!',  # nopep8
                                        detail=f'File: {path}')
                return
            self.csvFilePath_var.set(path)

    def open_chr_filedialog(self):
        """
        Open a filedialog to select a chromedriver
        """
        path = tk.filedialog.askopenfilename(
            parent=self,
            title=f'Select a chromedriver',
            initialfile='')
        if path:  # Path selected
            self.chrFilePath_var.set(path)

    def update_wraplengths(self, event):
        """
        Update the wraplengths for the path displayers
        """
        wraplength = event.widget.winfo_width() - 10
        ttk.Style().configure('Path.TLabel',
                              wraplength=wraplength)

    def network_analysis(self):
        """
        Save network analytics (network parameters and network centralities)
        """
        if self.interaction_var.get() == 'main':
            if self.edgeList_var.get() == 'letter':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_chainID.csv', header=None)
            if self.edgeList_var.get() == 'name':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_chainName.csv', header=None)
            if self.edgeList_var.get() == 'number':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_nodeID.csv', header=None)
        elif self.interaction_var.get() == 'detail':
            if self.edgeList_var.get() == 'letter':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_chainID_with_detail.csv', header=None)
            if self.edgeList_var.get() == 'name':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_chainName_with_detail.csv', header=None)
            if self.edgeList_var.get() == 'number':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_nodeID_with_detail.csv', header=None)
        G = nx.Graph()
        for i in range(len(edgelist_file)):
            G.add_edges_from([(edgelist_file.iloc[i, 0],
                               edgelist_file.iloc[i, 1])])
        n = {'PDB_ID': [self.proteinName_var.get()], 'Number of Nodes': [G.number_of_nodes()],
             'Number of Edges': [G.number_of_edges()],
             'Avg Degree': [sum(dict(G.degree).values()) / len(dict(G.degree))],
             'Avg Clustering Coefficient': [nx.average_clustering(G)],
             'Avg Path Length': [nx.average_shortest_path_length(G)]}
        network_parameters_df = pd.DataFrame(data=n)
        network_parameters_df.T.to_csv(self.proteinName_var.get(
        ) + '_network_parameters.csv', header=None, index=True)
        col_names = ['Network ID', 'Degree',
                     'Eigenvector Centrality', 'Betweenness Centrality']
        node_parameters_df = pd.DataFrame(columns=col_names)
        node_parameters_df['Degree'] = dict(G.degree).values()
        node_parameters_df['Network ID'] = dict(G.degree).keys()
        node_parameters_df['Eigenvector Centrality'] = nx.eigenvector_centrality(
            G).values()
        node_parameters_df['Betweenness Centrality'] = nx.betweenness_centrality(
            G).values()
        node_parameters_df = node_parameters_df.sort_values('Network ID')
        node_parameters_df['Eigenvector Centrality'] = node_parameters_df['Eigenvector Centrality'] / \
            sum(node_parameters_df['Eigenvector Centrality'])
        node_parameters_df.to_csv(self.proteinName_var.get(
        ) + '_network_centralities.csv', header=col_names, index=False)

    def plot_network(self):
        """
        Save network as image and open it
        """
        if self.interaction_var.get() == 'main':
            if self.edgeList_var.get() == 'letter':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_chainID.csv', header=None)
            if self.edgeList_var.get() == 'name':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_chainName.csv', header=None)
            if self.edgeList_var.get() == 'number':
                edgelist_file = pd.read_csv(
                    self.proteinName_var.get() + '_edgelist_nodeID.csv', header=None)
        elif self.interaction_var.get() == 'detail':
            if self.edgeList_var.get() == 'letter':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_chainID_with_detail.csv', header=None)
            if self.edgeList_var.get() == 'name':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_chainName_with_detail.csv', header=None)
            if self.edgeList_var.get() == 'number':
                edgelist_file = pd.read_csv(self.proteinName_var.get(
                ) + '_edgelist_nodeID_with_detail.csv', header=None)
        G = nx.Graph()
        for i in range(len(edgelist_file)):
            G.add_edges_from([(edgelist_file.iloc[i, 0],
                               edgelist_file.iloc[i, 1])])
        exec("nx.draw_{}(G, with_labels=True, node_size=80, font_size=8)".format(
            self.layout_type.get()))
        plt.savefig(self.proteinName_var.get() + '_network_graph.pdf')
        plt.savefig(self.proteinName_var.get() + '_network_graph.jpg')
        # Open image
        img = Image.open(self.proteinName_var.get() + '_network_graph.jpg')
        img.show()

    def run(self):
        """
        Run the automated algorithm
        """
        global nwd
        nwd = tk.filedialog.askdirectory()
        os.chdir(nwd)
        # -Get all variables-
        # Strings
        protein_name = self.proteinName_var.get()
        wanted_id = self.wantedProteinId_var.get()
        edge_list = self.edgeList_var.get()
        interaction = self.interaction_var.get()
        # File Paths
        pdb_file_path = self.pdbFilePath_var.get()
        csv_file_path = self.csvFilePath_var.get()
        driver_path = self.chrFilePath_var.get()

        # -Check for invalid paths-
        if not os.path.isfile(pdb_file_path):
            tk.messagebox.showwarning(master=self,
                                      title='Invalid Structure File',
                                      message='You have selected an invalid Structure file!\nPlease make sure that your Structure file still exists!')
            return

        if not os.path.isfile(csv_file_path):
            tk.messagebox.showwarning(master=self,
                                      title='Invalid CSV File',
                                      message='You have selected an invalid CSV file!\nPlease make sure that your CSV file still exists!')
            return

        if not os.path.isfile(driver_path):
            tk.messagebox.showwarning(master=self,
                                      title='Invalid Chromedriver',
                                      message='You have selected an invalid chromedriver!\nPlease make sure that your chromedriver still exists!')
            return

        # -Run algroithm-
        pisa = PISA_Protein(protein_name=protein_name,
                            pdb_file_path=pdb_file_path,
                            mapping_file_path=csv_file_path,
                            chrome_driver_path=driver_path,
                            wanted_protein_letter=wanted_id,
                            edge_list=edge_list)
        if interaction == 'main':
            pisa.scrape_chain_interaction()
            pisa.make_chain_edge_list()
        elif interaction == 'detail':
            pisa.make_residual_edgelist()
        pisa.organize_file(nwd)


if __name__ == "__main__":
    root = MainWindow()

    root.mainloop()


# change option
# add pictures
# change logo design
# add protein name to network centrality
# add headers for all output
