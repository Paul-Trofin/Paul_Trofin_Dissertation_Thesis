##############################################################
################ DELPHES MACRO FILES GENERATOR ###############
##############################################################
######### MACRO PYTHON FILE TO GENERATE .cmnd and .C #########
##### This script generates files for ./DelphesPythia8 #######
##############################################################
##################### Author: Paul Trofin ####################
##############################################################
### RUN LIKE THIS:
### python3 generate_delphes_macros.py
import os
                                                        
##############################################################
######################## OPTIONS #############################
##############################################################
### CREATE DIRECTORY AND THE FOLLWOING FILES WITHIN IT:
### input .cmnd file will keep the directory name
### analysis file .C file will be created with the name "get_variables.C"
### NAME OF THE DIRECTORY TO BE GENERATED
name = "ff_Z_ee"
### PROCESS NAME (matters only for printing)
hard_process = "Hard Process: f f~ -> Z (s-channel) -> e- e+"

#################################################################
################ OPTIONS FOR GENERATING .cmnd FILES #############
#################################################################
### NUMBER OF EVENTS
Nevents = "5000"
### BEAM SETTINGS
idA = "2212"
idB = "2212"
### CENTER OF MASS ENERGY
eCM = "13600"
### APPEND OPTIONS in PYTHIA8 FORMAT
options = []
options.append("")
### HARD PROCESS:
options.append("! Hard Process")
options.append("WeakSingleBoson:ffbar2ffbar(s:gmZ) = on")

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
banner_info = "Colliding: " + "(" + idA + ")" + " + " + "(" + idB + ")" + " at " + eCM + " GeV" 

print(" ______________________________________________________________")
print("                                                               ")
print("                   ___________________________                 ")
print("                  |                           |                ")
print("                  | DelphesPythia8 Simulation |                ")
print("                  |___________________________|                ")
print("                                                               ")
print("                     Author : Paul Trofin                      ")
print(" ______________________________________________________________")
print("                                                               ")
print(banner_info.center(66))
print("                                                              ")
print(hard_process.center(66))
print(" ______________________________________________________________")

### CREATE FOLDER
folder_path = name
os.makedirs(folder_path, exist_ok=True)

### WRITE THE CMND FILE
file_path = os.path.join(folder_path, name + ".cmnd")
root_path = file_path.replace(".cmnd", ".root")
log_path = file_path.replace(".cmnd", ".log")

### USE ABSOLUTE PATHS
abs_file_path = os.path.abspath(file_path)
abs_root_path = os.path.abspath(root_path)
abs_log_path = os.path.abspath(log_path)

with open(file_path, "w") as file:
    file.write("!!! COMMAND FILE FOR " + hard_process + "\n")
    file.write("\n")
    file.write(f"!!! Default card is ATLAS, change if you want.\n\n")
    file.write("!!! RUN LIKE THIS (from delphes installtion directory):\n")
    file.write(f"!!! ./DelphesPythia8 cards/delphes_card_ATLAS.tcl {abs_file_path} {abs_root_path} > {abs_log_path}\n")
    file.write("\n\n")

    file.write("! Number of events to generate\n")
    file.write("Main:numberOfEvents = " + Nevents + "\n")
    file.write("\n")

    file.write("! BEAM SETTINGS\n")
    file.write("Beams:idA = " + idA + "\n")
    file.write("Beams:idB = " + idB + "\n")
    file.write("Beams:eCM = " + eCM + "\n")
    file.write("\n")

    file.write("! PROCESS\n")
    for option in options:
        file.write(option + "\n")

print(f"** The folder {name} has been created.")
print(f"** Inside, the following have been generated:")
print(f"          ** COMMAND FILE:")
print(f"                 -> {name}.cmnd     (input file)")
print(f"          ** ANALYSIS FILE:")


##############################################################################
################# ROOT SCRIPT FOR CREATING ANALYSIS .C FILE ##################
##############################################################################
root_script = f'''
//////////////////////////////////////////////////////////////////////
///////////////////// EXTRACTS e-e+ VARIABLES ////////////////////////
/////////////// READS INPUT FROM DELPHES-ROOT FILE ///////////////////
//////////////////////////////////////////////////////////////////////
//// RUN LIKE THIS:
//// root -l get_variables.C'("{name}.root")'
//////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////
/////////////////////// LOAD  DELPHES LIBRARIES //////////////////////
//////////////////////////////////////////////////////////////////////
#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes.so)
#endif

#include "ExRootTreeReader.h"
#include "DelphesClasses.h"

//////////////////////////////////////////////////////////////////////
////////////////////////////// MAIN CODE /////////////////////////////
//////////////////////////////////////////////////////////////////////
void get_variables(const char *inputFile) {{

    // TChain
    TChain chain("Delphes");
    chain.Add(inputFile);

    // ExRootTreeReader
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    Long64_t Nevents = treeReader->GetEntries();

    //////////////////////////////////////////////////////////////////////
    /////////////////////// GET PARTICLES & JETS /////////////////////////
    //////////////////////////////////////////////////////////////////////
    // Get branches
    TClonesArray *branchElectron = treeReader->UseBranch("Electron");
    TClonesArray *branchJet = treeReader->UseBranch("Jet");
    TClonesArray *branchMissingET = treeReader->UseBranch("MissingET");

    //////////////////////////////////////////////////////////////////////
    //////////////////////////// CREATE TREES ////////////////////////////
    //////////////////////////////////////////////////////////////////////
	// Structures for branches
    struct P4 {{
        double E, Px, Py, Pz, Pt;
    }};
    struct Angle {{
        double eta, phi, theta;
    }};

    int N_electrons = 0, N_positrons = 0, N_electron_pairs = 0, N_jets = 0;
    double m_ee = 0, DielectronDeltaR = 0, MET = 0, Zjet_phi = 0, jets_mass = 0, Angle_between = 0;

    // Create trees
	TTree* Electrons = new TTree("Electrons", "");
    TTree* Positrons = new TTree("Positrons", "");
    TTree* ElectronPairs = new TTree("Dielectrons", "");
    TTree* Jets = new TTree("Jets", "");

    // Main branches for the number of entries
    Electrons->Branch("NumberOfElectrons", &N_electrons, "N_electrons/I");
    Positrons->Branch("NumberOfPositrons", &N_positrons, "N_positrons/I");
    ElectronPairs->Branch("NumberOfElectronPairs", &N_electron_pairs, "N_electron_pairs/I");
    Jets->Branch("JetMultiplicity", &N_jets, "N_jets/I");

    // Sub-branches
    P4 e_p4, e_bar_p4, Dielectron_p4, jet_p4;
    Angle e_angle, e_bar_angle, Dielectron_angle, jet_angle;
    Electrons->Branch("electron_p4", &e_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Electrons->Branch("electron_angle", &e_angle, "eta/D:phi/D:theta/D");
    Positrons->Branch("positron_p4", &e_bar_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Positrons->Branch("positron_angle", &e_bar_angle, "eta/D:phi/D:theta/D");
    ElectronPairs->Branch("DielectronMass", &m_ee, "m_ee/D");
    ElectronPairs->Branch("DielectronDeltaR", &DielectronDeltaR, "DielectronDeltaR/D");
    ElectronPairs->Branch("Dielectron_p4", &Dielectron_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    ElectronPairs->Branch("Dielectron_angle", &Dielectron_angle, "eta/D:phi/D:theta/D");
    ElectronPairs->Branch("Actual_phi", &Angle_between, "Actual_phi/D");
    Jets->Branch("jet_p4", &jet_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Jets->Branch("jet_angle", &jet_angle, "eta/D:phi/D:theta/D");
    Jets->Branch("JetMultiplicity", &N_jets, "N_jets/I");
    

    //////////////////////////////////////////////////////////////////////
    ////////////////////////// LOOP OVER EVENTS //////////////////////////
    //////////////////////////////////////////////////////////////////////
    for (int event = 0; event < Nevents; event++) {{
        treeReader->ReadEntry(event);
        std::vector<TLorentzVector> Selectrons, Spositrons, Sjets;

        //////////////////////////////////////////////////////////////////////
        //////////////////////// LOOP OVER PARTICLES /////////////////////////
        //////////////////////////////////////////////////////////////////////
        for (int i = 0; i < branchElectron->GetEntries(); i++) {{
            Electron *particle = (Electron*) branchElectron->At(i);
            TLorentzVector p4 = particle->P4();
            if (particle->Charge == -1) {{
                e_p4.E = p4.E();
                e_p4.Px = p4.Px();
                e_p4.Py = p4.Py();
                e_p4.Pz = p4.Pz();
                e_p4.Pt = p4.Pt();
                e_angle.eta = p4.Eta();
                e_angle.phi = p4.Phi();
                e_angle.theta = p4.Theta();
                Selectrons.push_back(p4);
                Electrons->Fill();
            }}
            if (particle->Charge == 1) {{
                e_bar_p4.E = p4.E();
                e_bar_p4.Px = p4.Px();
                e_bar_p4.Py = p4.Py();
                e_bar_p4.Pz = p4.Pz();
                e_bar_p4.Pt = p4.Pt();
                e_bar_angle.eta = p4.Eta();
                e_bar_angle.phi = p4.Phi();
                e_bar_angle.theta = p4.Theta();
                Spositrons.push_back(p4);
                Positrons->Fill();
            }}

        }}

        //////////////////////////////////////////////////////////////////////
        //////////////////////////////// PAIRS ///////////////////////////////
        //////////////////////////////////////////////////////////////////////       
        for (auto e : Selectrons) {{
            for (auto e_bar : Spositrons) {{
                TLorentzVector diel = (e + e_bar);
                m_ee = diel.M();
                Dielectron_p4.E = diel.E();
                Dielectron_p4.Px = diel.Px();
                Dielectron_p4.Py = diel.Py();
                Dielectron_p4.Pz = diel.Pz();
                Dielectron_p4.Pt = diel.Pt();
                Dielectron_angle.eta = diel.Eta();
                Dielectron_angle.phi = diel.Phi() + TMath::Pi();
                Dielectron_angle.theta = diel.Theta();
                DielectronDeltaR = std::sqrt((e.Eta() - e_bar.Eta())*(e.Eta() - e_bar.Eta()) + (e.Phi() - e_bar.Phi())*(e.Phi() - e_bar.Phi()));
                Angle_between = std::abs(e.Phi() - e_bar.Phi());
                ElectronPairs->Fill();
            }}
        }}

        //////////////////////////////////////////////////////////////////////
        //////////////////////////////// JETS ////////////////////////////////
        //////////////////////////////////////////////////////////////////////
        for (int i = 0; i < branchJet->GetEntries(); i++) {{
            Jet *jet = (Jet*) branchJet->At(i);
            TLorentzVector p4 = jet->P4();
            Sjets.push_back(p4);
        }}
        

        TLorentzVector total_jet;
        for (auto jet : Sjets) {{
            jet_p4.E = jet.E();
            jet_p4.Px = jet.Px();
            jet_p4.Py = jet.Py();
            jet_p4.Pz = jet.Pz();
            jet_p4.Pt = jet.Pt();
            jet_angle.eta = jet.Eta();
            jet_angle.phi = jet.Phi();
            jet_angle.theta = jet.Theta();
            Jets->Fill();
        }}

        if (Sjets.size() > 0) {{
            N_jets = Sjets.size();
            
        }}

    }}

    
    // SAVE histogram to file
    TFile outFile("variables.root", "RECREATE");
    Electrons->Write();
    Positrons->Write();
    ElectronPairs->Write();
    Jets->Write();
    outFile.Close();

    // Clean up
    delete treeReader;
}}
//////////////////////////////////////////////////////////////////////
'''
### Create the ROOT analysis file and write the contents 
root_file_path = os.path.join(folder_path, "get_variables.C")
with open(root_file_path, "w") as root_file:
    root_file.write(root_script)

print(f"                 -> get_variables.C  (extract kinematic variables)")
