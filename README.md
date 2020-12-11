# LouiseNet
LousieNet automates the process of extracting interactions among different components present in a PDB file based upon their shared buried interfaces calculated by the PISA web portal. Next, LouiseNet performs the fundamental network analysis of the macromolecular machines’ structures based upon the interactions observed between the PDB chains using PISA.

To Run LouiseNet:

for Win10: downlaod "LouiseNet_win_exe" and launch "LouiseNet.exe"

for MacOS: downlaod "LouiseNet_mac_app" and launch "main" (coming 12/15/20)

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
