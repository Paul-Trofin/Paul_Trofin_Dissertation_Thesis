##############################################################
######### MACRO PYTHON FILE TO GENERATE .cmnd and .cc ########
########## Only for Pythia: analyses crossx data  ############
##############################################################
import os
                                                        
##############################################################
######################## OPTIONS #############################
##############################################################
### NAME 
name = "ff_gmZ"
### CM ENERGY RANGE
eCM_ranges = [
    (20, 80, 5),
    (80, 87, 1),
    (87, 95, 0.3),
    (95, 100, 1),
    (100, 240, 5),
]
### NUMBER OF EVENTS
Nevents = "5000"
### BEAM SETTINGS
idA = "11"
idB = "-11"
### PROCESS in PYTHIA8 FORMAT
options = []
options.append("")
options.append("! Hard Process")
options.append("WeakSingleBoson:ffbar2gmZ = on")

# Weak gmZ Mode
options.append("WeakZ0:gmZmode = 0 ! choose gamma*/Z0")

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
options.append("! Force Z decays to e-e+")
options.append("23:onMode = off")
options.append("23:onIfAll = 11 -11")
options.append("")

# Create the output directory if it doesn't exist
output_dir = f"{name}"
os.makedirs(output_dir, exist_ok=True)

# Loop over the ranges in eCM_ranges and generate .cmnd files for each energy range
for eCM_range in eCM_ranges:
    eCM_begin, eCM_end, eCM_step = eCM_range
    
    # Start from eCM_begin and loop until eCM_end with the specified step
    eCM = eCM_begin
    while eCM <= eCM_end:
        # Create the .cmnd file for each energy value
        cmnd_file = os.path.join(output_dir, f"{eCM:.1f}.cmnd")  # Format to 1 decimal place
        
        with open(cmnd_file, "w") as file:
            # Write the common settings to the file
            file.write(f"! Number of events to generate\n")
            file.write(f"Main:numberOfEvents = {Nevents}\n\n")
            
            # Beam settings with the current eCM
            file.write(f"! BEAM SETTINGS\n")
            file.write(f"Beams:idA = {idA}\n")
            file.write(f"Beams:idB = {idB}\n")
            file.write(f"Beams:eCM = {eCM:.1f}\n\n")  # Format to 1 decimal place
            
            # Write the process-specific settings
            for option in options:
                file.write(option + "\n")
        
        # Increment eCM by the step value (float step is supported here)
        eCM += eCM_step


print("All .cmnd files have been generated successfully!")

file_Makefile = f'''
# MAKEFILE TO COMPILE PYTHIA8
%: %.cc
	g++ -I/home/paul/pythia/pythia8310/include `root-config --cflags` $< -o $@ -L/home/paul/pythia/pythia8310/lib `root-config --glibs` -lpythia8

# make clean
clean:
	rm -f $(basename $(wildcard *.cc))
'''
file_path_Makefile = os.path.join(name, "Makefile")
with open(file_path_Makefile, "w") as out_Makefile:
    out_Makefile.write(file_Makefile)

file_cc = f"""
#include "Pythia8/Pythia.h"
#include <iostream>
#include <dirent.h>
#include <string>
#include <fstream>
#include <map>
#include <iomanip>  // for setprecision

using namespace Pythia8;
using namespace std;

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
        cerr << "Error opening directory." << endl;
    }}
}}

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

    for (const auto& cmndFile : cmndFiles) {{
        cout << "Processing file: " << cmndFile << endl;

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

    ofstream outFile("{name}_crossx.dat");
    outFile << fixed << setprecision(1);
    outFile << "eCM (GeV)\\t\\tCrossX (fb)" << endl;
    for (const auto& entry : crossSections) {{
        outFile << entry.first << "\\t\\t\\t" << entry.second << endl;
    }}
    outFile.close();

    return 0;
}}
"""


# Write the .cc file to the same directory
file_path_cc = os.path.join(name, f"{name}.cc")
with open(file_path_cc, "w") as out_cc:
    out_cc.write(file_cc)

print(f"Generated: {file_path_cc}")

# Write ROOT macro for plotting cross section
file_plot_macro = f"""
////////////////////////////////////////////////////////////////////////
////////////// TAKES AS INPUT CROSSX .dat FILES ////////////////////////
////////////////////////////////////////////////////////////////////////
// RUN LIKE THIS:
// root -l plot_crossx.C'("{name}_crossx.dat")'
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
    graph->Draw("APL");

    c1->SaveAs("{name}_crossx.png");
}}"""

file_path_plot = os.path.join(name, "plot_crossx.C")
with open(file_path_plot, "w") as out_plot:
    out_plot.write(file_plot_macro)

print(f"Generated: plot_crossx.C")
