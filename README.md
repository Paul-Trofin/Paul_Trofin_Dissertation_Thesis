__________________________________________________________________________
|                                                                        |
|               Macro Files Generators & Other Scripts                   |           
|                                                                        |
|                        Author: Paul Trofin                             |
|________________________________________________________________________|

All  of  the  scripts  presented  here are used for my dissertation thesis
"Z Boson Production ...". 

This   GitHub   Repository  contains  multiple  folders.  Each  folder  is
dedicated to one type of generator:

________________________________________________________________________
***** Pythia8 Macro Files Generator (single python file)
________________________________________________________________________

  ***  Used for fast  estimation  of  processes  cross sections profile
  
  ***  Generates  a folder  with the desired name and specific process,
       in which the following will be generated:
       will be generated:
    -> ".cmnd"  files  in  the  desired  center  of  mass  energy range 
    -> a ".cc"  to  compile  and  run Pythia8 that writes a ".dat" file
       which contains Cross Section (fb) vs Center of Mass Energy (GeV)
    -> Generates a ROOT ".C" to plot the cross section (y-axis) vs. the
       center of mass energy (x-axis)
       
  ***  RUN LIKE THIS:
       -> python3 generate_pythia8_macros
  ***  For  more   information   please  refer  to  the  README  in  the
        dedicated folder "Pythia8_Macro_Files_Generator".
________________________________________________________________________
