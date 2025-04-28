                           TO BE UPDATED !!!
__________________________________________________________________
               Macro Files Generators & Other Scripts

                          Author: Paul Trofin
___________________________________________________________________

All of the scripts presented here are used for my dissertation
thesis "Z Boson Production ...".

This GitHub Repository contains two folders. Each folder
is dedicated to one of the following python generators:

__________________________________________________________________
                     Pythia8 Macro Files Generator
                            ~one python file~
__________________________________________________________________

  ***  Used  for  calculating cross sections  for a given center
       of mass energy range.
  
  ***  Generates  a folder  with the desired name  in which the
       following will be generated:
       
    -> ".cmnd" files in the desired center of mass energy range;
    -> A ".cc" to compile and run Pythia8 which then writes
       a ".txt" file containing Cross Section (fb) vs Center of
       Mass Energy (GeV);
    -> Generates a ROOT ".C" to plot the cross section (y-axis)
       vs. the center of mass energy (x-axis);
       
  ***  RUN LIKE THIS:
       -> python3 generate_pythia8_macros
  ***  For more information on how  to use it please refer to
       the README in the dedicated folder:
       "Pythia8_Macro_Files_Generator"
__________________________________________________________________

__________________________________________________________________
                     Delphes Macro Files Generator
                            ~one python file~
__________________________________________________________________

  ***  Used for fast generation of input command file (.cmnd) and 
       ROOT analysis file (.C) for ./DelphesPythia8 executable
  
  ***  Generates  a folder  with the desired name  in which the
       following will be generated:
       
    -> A .cmnd file containing the desired Pythia8 settings for 
       generating HEP events, including detector response.
    -> A ROOT ".C" file for analysis. It extracts information
       from the output delphes file (.root) and creates another
       file (.root) containing the kinematic variables used for
       analyzing the dielectrons final state.  
       
  ***  RUN LIKE THIS:
       -> python3 generate_delphes_macros
  ***  For more information on how  to use it please refer to
       the README in the dedicated folder:
       "Delphes_Macro_Files_Generator"
______________________________________________________________________
