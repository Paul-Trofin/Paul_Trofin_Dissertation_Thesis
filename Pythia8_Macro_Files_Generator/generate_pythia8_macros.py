##############################################################
################ PYTHIA8 MACRO FILES GENERATOR ###############
##############################################################
######### MACRO PYTHON FILE TO GENERATE .cmnd and .cc ########
########## Only for Pythia: analyses crossx data  ############
##############################################################
##################### AUTHOR: Paul Trofin ####################
##############################################################
### RUN LIKE THIS:
### python3 generate_pythia8_macros.py

import os
                                                        
##############################################################
######################## OPTIONS #############################
##############################################################
### CREATE DIRECTORY WITH THE FOLLWOING FILES:
### (.cmnd file will have the name: <eCM>.cmnd)
### (.cc file will have the name: <name>.cc)
### (.txt file will have the name: <name>_crossx.txt)
### (.png file will have the name: <name>_crossx.png)
### NAME OF THE DIRECTORY TO BE GENERATED
name = "ee_Z_ee"
eCM_ranges = [
    # for each interval:
    # start eCM, end eCM, step size
    (20, 60, 5),         
    (60, 85, 2),         
    (85, 88, 0.5),       
    (88, 90.5, 0.2),     
    (90.5, 91.5, 0.1),   
    (91.5, 93, 0.2),     
    (93, 96, 0.5),       
    (96, 110, 2),        
    (110, 240, 5)
    # Add or substract as many as you like
    # Min step size: 0.1 GeV        
]

#################################################################
################ OPTIONS FOR GENERATING .cmnd FILES #############
#################################################################
### MAIN OPTIONS:
### NUMBER OF EVENTS
Nevents = "5000"
### BEAM SETTINGS
idA = "11"
idB = "-11"
### APPEND OPTIONS in PYTHIA8 FORMAT
options = []
options.append("")
### HARD PROCESS:
options.append("! Hard Process")
options.append("WeakSingleBoson:ffbar2gmZ = on")

### OPTIONAL SETTINGS
# Weak gmZ Mode
options.append("WeakZ0:gmZmode = 2 ! choose Z")

### PARTON LEVEL
options.append("")
options.append("! Parton Level")
options.append("PartonLevel:MPI = off")
options.append("PartonLevel:ISR = off")
options.append("PartonLevel:FSR = off")

### HADRON LEVEL
options.append("")
options.append("! Hadron Level")
options.append("HadronLevel:Hadronize = on")

### DECAY OPTIONS
options.append("")
options.append("! Force Z decays to e- e+")
options.append("23:onMode = off")
options.append("23:onIfAll = 11 -11")

#################################################################
######### END OF OPTIONS PART. CHANGE MANUALLY FROM HERE. #######
#################################################################

### CREATE DIRECTORY
output_dir = f"{name}"
os.makedirs(output_dir, exist_ok=True)

#### LOOP OVER eCM RANGES
for eCM_range in eCM_ranges:
    eCM_begin, eCM_end, eCM_step = eCM_range
    
    ### WRITE THE .cmnd FILES
    eCM = eCM_begin
    while eCM <= eCM_end:
        ### CREATE THE .cmnd FILE
        cmnd_file = os.path.join(output_dir, f"{eCM:.1f}.cmnd") 
                                    # Format to 1 decimal place
        
        with open(cmnd_file, "w") as file:
            ### WRITE THE HEADER
            file.write(f"! Number of events to generate\n")
            file.write(f"Main:numberOfEvents = {Nevents}\n\n")
            
            ### WRITE THE BEAM SETTINGS
            file.write(f"! BEAM SETTINGS\n")
            file.write(f"Beams:idA = {idA}\n")
            file.write(f"Beams:idB = {idB}\n")
            file.write(f"Beams:eCM = {eCM:.1f}\n\n")
            
            ### WRITE THE OPTION ONE BY ONE
            for option in options:
                file.write(option + "\n")
        
        ### INCREMENT THE eCM
        eCM += eCM_step



#################################################################
############################ MAKEFILE ###########################
#################################################################
### THIS PART WILL CREATE A MAKEFILE TO COMPILE THE .cc FILE
file_Makefile = f'''
# MAKEFILE TO COMPILE PYTHIA8
# Assumes these are exported to PATH, such that they are set in the environment:
# export PYTHIA8=<Pythia8_installation_directory>
# export PATH=$PATH:$PYTHIA8/bin
# export PYTHIA8_INCLUDE=$PYTHIA8/include
# export PYTHIA8_LIBRARY=$PYTHIA8/lib/libpythia8.so
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PYTHIA8/lib

# Variables (use environment variables)
PYTHIA8_INCLUDE_PATH ?= $(PYTHIA8_INCLUDE)
PYTHIA8_LIB_PATH ?= $(dir $(PYTHIA8_LIBRARY))

%: %.cc
	g++ -I$(PYTHIA8_INCLUDE_PATH) `root-config --cflags` $< -o $@ -L$(PYTHIA8_LIB_PATH) `root-config --glibs` -lpythia8

# make clean
clean:
	rm -f $(basename $(wildcard *.cc))

'''
### WRITE THE MAKEFILE
file_path_Makefile = os.path.join(name, "Makefile")
with open(file_path_Makefile, "w") as out_Makefile:
    out_Makefile.write(file_Makefile)

print(" ______________________________________________________________")
print("                                                               ")
print("                _________________________________              ")
print("               |                                 |             ")
print("               |  Pythia8 Macro Files Generator  |             ")
print("               |_________________________________|             ")
print("                                                               ")
print("                                                               ")
print("                     Author : Paul Trofin                      ")
print("_______________________________________________________________")
print("                                                               ")
print(f"*** The folder {name} has been generated.")
print("*** Inside are the following:")
print("    -> All input .cmnd files in the desired interval ranges.")
print("    -> Makefile (please change to your Pythia8 lib & include)")
print("    -> .cc file for running Pythia8")
print("    -> ROOT .C file to plot Crossx vs. eCM")
print("                                                               ")
print(f"*** Please refer to the README in this directory for more information.")
print("_______________________________________________________________")

#################################################################
######################### PYTHIA8 .cc FILE ######################
#################################################################
### THIS PART WILL CREATE A .cc FILE TO EXTRACT THE CROSS SECTION
### FROM THE .cmnd FILES and WRITE THEM TO A .txt FILE
### NO OPTIONS FOR THIS PART -- YOU CAN CHANGE MANUALLY
file_cc = f"""
//////////////////////////////////////////////////////////////
////// MACRO .cc FILE TO GENERATE AND EXTRACT CROSSX /////////
//////////////////////////////////////////////////////////////
///////////////////// AUTHOR: Paul Trofin ////////////////////
//////////////////////////////////////////////////////////////
// RUN LIKE THIS:
// make {name}
// ./{name} > {name}.log
#include "Pythia8/Pythia.h"
#include <iostream>
#include <dirent.h>
#include <string>
#include <fstream>
#include <map>
#include <iomanip>

using namespace Pythia8;
using namespace std;

// FUNCTION TO READ .cmnd FILES FROM WORKING DIRECTORY
void readCmndFiles(vector<string>& cmndFiles) {{
    DIR* dir = opendir(".");
    if (dir) {{
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {{
            string filename = entry->d_name;
            if (filename.substr(filename.find_last_of(".") + 1) == "cmnd") {{
                cmndFiles.push_back(filename);
            }}
        }}
        closedir(dir);
    }} else {{
        cerr << "Error opening working directory." << endl;
    }}
}}

// FUNCTION TO EXTRACT CM ENERGY FROM .cmnd FILENAMES
double extractCMEnergy(const string& filename) {{
    size_t pos = filename.find(".cmnd");
    if (pos != string::npos) {{
        string base = filename.substr(0, pos);
        try {{
            return stod(base);  // parse as double
        }} catch (...) {{
            cerr << "Error: Could not parse CM energy from filename " << filename << endl;
            return -1.0;
        }}
    }} else {{
        cerr << "Error: Invalid filename format: " << filename << endl;
        return -1.0;
    }}
}}

int main() {{
    Pythia pythia;
    Event& event = pythia.event;

    vector<string> cmndFiles;
    readCmndFiles(cmndFiles);

    map<double, double> crossSections;
	
	int cmnds_done = 0;
    for (const auto& cmndFile : cmndFiles) {{
        cerr << "Processing file: " << cmndFile << endl;
        cmnds_done ++;
        cerr << "Remaining .cmnd files: " << cmndFiles.size() - cmnds_done;
        cerr << endl << endl;

        pythia.readFile(cmndFile);
        int nEvents = pythia.mode("Main:numberOfEvents");
        pythia.init();

        for (int i = 0; i < nEvents; ++i) {{
            if (!pythia.next()) continue;
        }}

        pythia.stat();
        double totalCrossSection = pythia.info.sigmaGen();
        double cmEnergy = extractCMEnergy(cmndFile);

        crossSections[cmEnergy] = totalCrossSection * 1e12;  // Convert to fb
    }}

    ofstream outFile("{name}_crossx.txt");
    outFile << fixed << setprecision(1);
    outFile << "eCM (GeV)\\t\\tCrossX (fb)" << endl;
    for (const auto& entry : crossSections) {{
        outFile << entry.first << "\\t\\t\\t" << entry.second << endl;
    }}
    outFile.close();
    cerr << "Cross section data written to {name}_crossx.txt" << endl;

    return 0;
}}
"""


### WRITE THE .cc FILE
file_path_cc = os.path.join(name, f"{name}.cc")
with open(file_path_cc, "w") as out_cc:
    out_cc.write(file_cc)

##############################################################
######## ROOT .C FILE TO PLOT CROSSX FROM .TXT FILE ##########
##############################################################
### NO OPTIONS HERE -- CHANGE MANUALLY
### Dissertation plots have been generated with this .C script
### modified to include legend and other functions 
file_plot_macro = f"""
////////////////////////////////////////////////////////////////////////
///////////////// TAKES AS INPUT CROSSX .txt FILES /////////////////////
///////////////// GENERATES <file_name>_crossx.png /////////////////////
////////////////////////////////////////////////////////////////////////
//////////////////////// AUTHOR: Paul Trofin ///////////////////////////
////////////////////////////////////////////////////////////////////////
// Dissertation plots have been generated with this .C script
// modified to include legend and other functions
// RUN LIKE THIS:
// root -l plot_crossx.C'("{name}_crossx.txt")'
void plot_crossx(std::string inputFile) {{
    std::ifstream infile(inputFile);
    if (!infile.is_open()) {{
        std::cerr << "Error: Could not open " << inputFile << std::endl;
        return;
    }}

    std::vector<double> eCM, crossX;
    std::string header;
    std::getline(infile, header);

    double e, x;
    while (infile >> e >> x) {{
        eCM.push_back(e);
        crossX.push_back(x);
    }}

    int n = eCM.size();
    if (n == 0) {{
        std::cerr << "No data found in " << inputFile << std::endl;
        return;
    }}

    auto graph = new TGraph(n, &eCM[0], &crossX[0]);
    graph->SetTitle("");
    graph->SetMarkerStyle(20);
    graph->SetMarkerSize(1.0);
    graph->SetLineWidth(2);
    graph->SetLineColor(kBlue + 2);
    graph->SetMarkerColor(kBlack);
    graph->GetXaxis()->SetTitle("Center of Mass Energy (GeV)");
    graph->GetYaxis()->SetTitle("Cross Section (fb)");

    auto c1 = new TCanvas("c1", "Cross Section Plot", 800, 600);
    c1->SetGrid();
    graph->Draw("AP");

    c1->SaveAs("{name}_crossx.png");
}}"""

### WRITE THE PLOT .C FILE
file_path_plot = os.path.join(name, "plot_crossx.C")
with open(file_path_plot, "w") as out_plot:
    out_plot.write(file_plot_macro)
