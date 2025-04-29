
//////////////////////////////////////////////////////////////////////
///////////////// GENERATE ANALYSIS TREE VARIABLES ///////////////////
/////////////// READS INPUT FROM DELPHES-ROOT FILE ///////////////////
//////////////////////////////////////////////////////////////////////
//// This script is essentially the same as the get_variables.C
//// It changes only when the Dielectrons is filled
//// Basically, it fakes pile-up for dielectrons coming from single W+-
//// This would work because the events of producing an e- or an e+ are
//// uncorellated. 
//// Because there are way to many e-e+ pairs, it stores the closest
//// dielectronic mass to that of the Z^0
//// Use for processes in which a single electron/positron is produced
//// and you want to fake pile-up.
//// RUN LIKE THIS:
//// root -l get_variables_w.C'("ff_W_enu.root")'
//////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////
///////////////////////////// LIBRARIES //////////////////////////////
//////////////////////////////////////////////////////////////////////
#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes.so)
#endif

#include "ExRootTreeReader.h"
#include "DelphesClasses.h"

//////////////////////////////////////////////////////////////////////
////////////////////////////// MAIN CODE /////////////////////////////
//////////////////////////////////////////////////////////////////////
void get_variables_w(const char *inputFile) {

    // TChain
    TChain chain("Delphes");
    chain.Add(inputFile);

    // ExRootTreeReader
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    Long64_t Nevents = treeReader->GetEntries();

    //////////////////////////////////////////////////////////////////////
    /////////////////////// GET PARTICLES & JETS /////////////////////////
    //////////////////////////////////////////////////////////////////////
    TClonesArray *branchElectron = treeReader->UseBranch("Electron");
    TClonesArray *branchJet = treeReader->UseBranch("Jet");
    TClonesArray *branchMissingET = treeReader->UseBranch("MissingET");

    //////////////////////////////////////////////////////////////////////
    //////////////////////////// CREATE TREES ////////////////////////////
    //////////////////////////////////////////////////////////////////////
	// Electrons Tree
    struct P4 {
        double E, Px, Py, Pz, Pt;
    };
    struct Angle {
        double eta, phi, theta;
    };

    int N_electrons = 0, N_positrons = 0, N_electron_pairs = 0, N_jets = 0;
    double m_ee = 0, deltaR_ee = 0, MET = 0, Zjet_phi = 0, jets_mass = 0, best_deltaR_ee = 0, best_Z_pT = 0;

	TTree* Electrons = new TTree("Electrons", "");
    TTree* Positrons = new TTree("Positrons", "");
    TTree* ElectronPairs = new TTree("Dielectrons", "");
    TTree* Jets = new TTree("Jets", "");
    TTree* BDT = new TTree("BDT", "");

    // Main branches for the number of entries
    Electrons->Branch("NumberOfElectrons", &N_electrons, "N_electrons/I");
    Positrons->Branch("NumberOfPositrons", &N_positrons, "N_positrons/I");
    ElectronPairs->Branch("NumberOfElectronPairs", &N_electron_pairs, "N_electron_pairs/I");
    Jets->Branch("JetMultiplicity", &N_jets, "N_jets/I");

    // Sub-branches
    P4 e_p4, e_bar_p4, Z_p4, jet_p4;
    Angle e_angle, e_bar_angle, Z_angles, jet_angle;
    Electrons->Branch("electron_p4", &e_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Electrons->Branch("electron_angle", &e_angle, "eta/D:phi/D:theta/D");
    Positrons->Branch("positron_p4", &e_bar_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Positrons->Branch("positron_angle", &e_bar_angle, "eta/D:phi/D:theta/D");
    ElectronPairs->Branch("DielectronMass", &m_ee, "m_ee/D");
    ElectronPairs->Branch("DielectronDeltaR", &deltaR_ee, "deltaR_ee/D");
    ElectronPairs->Branch("Dielectron_p4", &Z_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    ElectronPairs->Branch("Dielectron_angle", &Z_angles, "eta/D:phi/D:theta/D");
    Jets->Branch("jet_p4", &jet_p4, "E/D:Px/D:Py/D:Pz/D:Pt/D");
    Jets->Branch("jet_angle", &jet_angle, "eta/D:phi/D:theta/D");
    Jets->Branch("JetMultiplicity", &N_jets, "N_jets/I");
    BDT->Branch("best_deltaR_ee", &best_deltaR_ee, "best_deltaR_ee/D");
    BDT->Branch("best_Z_pT", &best_Z_pT, "best_Z_pT/D"); 
    BDT->Branch("JetMultiplicity", &N_jets, "N_jets/I");
    
    std::vector<TLorentzVector> final_e, final_e_bar;
    //////////////////////////////////////////////////////////////////////
    ////////////////////////// LOOP OVER EVENTS //////////////////////////
    //////////////////////////////////////////////////////////////////////
    for (int event = 0; event < Nevents; event++) {
        treeReader->ReadEntry(event);
        std::vector<TLorentzVector> Selectrons, Spositrons, Sjets;

        //////////////////////////////////////////////////////////////////////
        //////////////////////// LOOP OVER PARTICLES /////////////////////////
        //////////////////////////////////////////////////////////////////////
        for (int i = 0; i < branchElectron->GetEntries(); i++) {
            Electron *particle = (Electron*) branchElectron->At(i);
            TLorentzVector p4 = particle->P4();
            if (particle->Charge == -1) {
                e_p4.E = p4.E();
                e_p4.Px = p4.Px();
                e_p4.Py = p4.Py();
                e_p4.Pz = p4.Pz();
                e_p4.Pt = p4.Pt();
                e_angle.eta = p4.Eta();
                e_angle.phi = p4.Phi();
                e_angle.theta = p4.Theta();
                Selectrons.push_back(p4);
                final_e.push_back(p4);
                
                Electrons->Fill();
            }
            if (particle->Charge == 1) {
                e_bar_p4.E = p4.E();
                e_bar_p4.Px = p4.Px();
                e_bar_p4.Py = p4.Py();
                e_bar_p4.Pz = p4.Pz();
                e_bar_p4.Pt = p4.Pt();
                e_bar_angle.eta = p4.Eta();
                e_bar_angle.phi = p4.Phi();
                e_bar_angle.theta = p4.Theta();
                Spositrons.push_back(p4);
                final_e_bar.push_back(p4);
                Positrons->Fill();
            }

        }

        //////////////////////////////////////////////////////////////////////
        //////////////////////////////// JETS ////////////////////////////////
        //////////////////////////////////////////////////////////////////////
        for (int i = 0; i < branchJet->GetEntries(); i++) {
            Jet *jet = (Jet*) branchJet->At(i);
            TLorentzVector p4 = jet->P4();
            Sjets.push_back(p4);
        }
        

        TLorentzVector total_jet;
        for (auto jet : Sjets) {
            jet_p4.E = jet.E();
            jet_p4.Px = jet.Px();
            jet_p4.Py = jet.Py();
            jet_p4.Pz = jet.Pz();
            jet_p4.Pt = jet.Pt();
            jet_angle.eta = jet.Eta();
            jet_angle.phi = jet.Phi();
            jet_angle.theta = jet.Theta();
            Jets->Fill();
        }

        if (Sjets.size() > 0) {
            N_jets = Sjets.size();
            
        }

        BDT->Fill();
    }

    //////////////////////////////////////////////////////////////////////
    //////////////////////////////// PAIRS ///////////////////////////////
    //////////////////////////////////////////////////////////////////////
    TLorentzVector best_Z;
    // BUFFER
    int max_loop = 100000;      
    for (auto e : final_e) {
        for (auto e_bar : final_e_bar) {
            TLorentzVector Z = (e + e_bar);
            m_ee = Z.M();
            Z_p4.E = Z.E();
            Z_p4.Px = Z.Px();
            Z_p4.Py = Z.Py();
            Z_p4.Pz = Z.Pz();
            Z_p4.Pt = Z.Pt();
            Z_angles.eta = Z.Eta();
            Z_angles.phi = std::abs(e.Phi() - e_bar.Phi());
            Z_angles.theta = Z.Theta();
            deltaR_ee = std::sqrt((e.Eta() - e_bar.Eta())*(e.Eta() - e_bar.Eta()) + (e.Phi() - e_bar.Phi())*(e.Phi() - e_bar.Phi()));
            ElectronPairs->Fill();

            // Store best electron positron pair for BDT
            if (std::abs(Z.M() - 91.2) < std::abs(best_Z.M() - 91.2)) {
                best_Z = Z;
                best_deltaR_ee = deltaR_ee;
                best_Z_pT = Z.Pt();
            }
            max_loop--;
            if (max_loop <= 0) {
                break;
            }
        }
    }
    
    // SAVE histogram to file
    TFile outFile("variables.root", "RECREATE");
    Electrons->Write();
    Positrons->Write();
    ElectronPairs->Write();
    Jets->Write();
    BDT->Write();
    outFile.Close();

    // Clean up
    delete treeReader;
}
//////////////////////////////////////////////////////////////////////
