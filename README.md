# LouiseNet
LousieNet automates the process of extracting interactions among different components present in a PDB file based upon their shared buried interfaces calculated by the PISA web portal. Next, LouiseNet performs the fundamental network analysis of the macromolecular machines’ structures based upon the interactions observed between the PDB chains using PISA.

To Run LouiseNet:

for Win10: download "LouiseNet.exe" and launch "LouiseNet.exe"

for MacOS: LouiseNet will need to be run from a terminal window using Python, instructions are below. Note that the MacOS version is only compatible with PDB/CIF files from cryo-EM data (no crystallographic symmetry information). The Windows version can accept structural files determined from either cryo-EM or crystallographic data.

IMPORTANT: The mapping file must be in .csv format! See "example.csv" for an example. If you use the spliceosome example files, make sure that the files are .csv (they may need to be opened in Excel and saved in .csv format). 

NOTE: For instructional videos for both Win10 and MacOS/Python, visit https://uwmadison.box.com/v/LouiseNetVideos

1.	Options:
------------
LouiseNet allows users to select one of the network types under options 1.a panel.

1.a  Select Network Type: Users have the freedom to use the Chain only network or Chain & Residue network.
Chains only selection will identify the interactions between the individual chains present in the PDB file.  Whereas Chains & Residues option will sort out the interactions between the selected chain residues with rest of the chains present in the PDB file.

1.b Select Edgelist Output: This selection provides possible choices for the edgelist format
Chain ID will generate an edgelist labeled by the letters denoted for PDB chains ID. Chain Name will generate an edgelist labeled by protein names. Node ID will create an edgelist labeled by node IDs (numeric Ids). A mapping file of chain name/chain ID/node ID will be saved in the output folder of the users’ naming (in panel 3.a). These various edgelist options will provide users freedom to perform further network analysis independently based upon users’ applications.

2.	Upload Files:
------------
2.a Select Structure File: Users should upload the PDB file. 

2.b Select Mapping File: Users should upload a CSV format mapping file without a header, where  : 1st column should represent the Chain Name, and 2nd column represent the corresponding Chain ID in the PDB file.

2.c Select Chrome Driver:  Select chrome driver that is up to date with the version of Google Chrome. For example: Chrome Driver 85.0.4183.87 will work for Google Chrome Version 85.0.4183.121 (download Chrome Driver at: https://chromedriver.chromium.org )

3.	Structure Info: 
------------
This panel asks users to enter the Structure (PDB) File Name for the output folder  and Chain ID  for the chain which would be used for residue level network analysis as defined in panel 1.a.

4.	Select Directory & Run: 
------------
This panel will allow the users to select a directory for the output folder and sorted out interactions from the PISA in terms of edgelist will be saved in the output folder of the users’ naming (in panel 3.a).

!!! Do not move the output folder until everything is finished running!!!


5.	Plot Network:
------------
This panel will allow users to plot the protein- protein interaction network derived from PDB structure file in seven different layouts: circular, planar, kanada_kawai, random, spectral, spring and shell. Users can select a network layout type (default circular), then click “Plot Network” to generate a network plot. Finally, network structure plot and where will it be saved as a pdf file and a jpg file in the output folder of the users’ naming (in panel 3.a).

!!! Do not move the output folder until everything is finished running!!!

6.	Network Analysis: 
------------
Network analysis calculates the topological network parameters of the network such as average degree, average clustering coefficient, and average shortest path length. Additionally, three types of centralities (degree, eigenvector, and betweenness) are calculated for each node in a network. The csv output file containing network parameters, and centralities values are saved in the user-specified output folder.

!!! Do not move the output folder until everything is finished running!!!

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSTALLATION INSTRUCTIONS FOR MACOS/PYTHON

1. Python 3.9 and pip (required to install other python libraries) installation
------------
Download and install python3.9: https://www.python.org/ftp/python/3.9.6/python-3.9.6-macosx10.9.pkg 
Install pip via terminal
type and run:  python -m ensurepip --upgrade

Install required packages:
BeautifulSoup
Selenium
Pandas
Networkx
Matplotlib
PIL
			For each required package please go to terminal and type the following:
				1) pip3 install beautifulsoup4
				
				2) pip3 install selenium
				
				3) pip3 install pandas
				
				4) pip3 install networkx
				
				5) pip3 install matplotlib
				
				6) sudo pip install pillow

2. Run script
------------
Make sure all three scripts (CustomTkinterWidgets, LouiseNet_backend, and run_me) and the img folder are all in the same folder
Find the script path of run_me.py
Right click on the “run_me.py” file
Press and hold option, then the option “copy ’run_me.py ’’ as pathname” will appear 
Click on it to copy pathname
Run script via terminal
Type “python3 (insert scriptpath)”
Run the script

