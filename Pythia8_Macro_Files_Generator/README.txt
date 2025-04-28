                           
                           TO BE UPDATED !!!   
________________________________________________________________
                    
                     Pythia8 Macro Files Generator
                            ~one python file~
________________________________________________________________

  *** This python script stands as the base code for
      generating the required files to run Pythia8 and
      extract the cross section in a given center of mass
      energy range.
	  
  *** The first part of "generate_pythia8_macros.py"
      contains the options section in which you enter
      {name} - will be the name of the folder in which the
      {name}.cc, Makefile, plot_crossx.C, and all the .cmnd
      files will be generated.
	  
      -> .cmnd files will have the name {eCM}.cmnd; the only
         parameter that is changing in each .cmnd is the eCM,
         the rest of the options are the same for all of them;
         the options are written in the .cmnds by appending
         them one by one;
	  
      -> .cc is generated automatically the same (no explicit
         options), but you can change it manually to suit your
         needs; this file is used for running Pythia8 and
         writing the calculated cross section to
         {name}_crossx.txt;
		 
      -> Makefile is used for the compilation process
	  
      -> plot_crossx.C takes as input the {name}_crossx.txt and
         plots the Cross Section (fb) vs. Center of Mass Energy
         (GeV);
________________________________________________________________
  *** Let's run the default example step by step:
  	  
      -> python3 generate_pythia8_macros.py (ee_Z_ee folder
         should be created.)
  	 
      -> cd ee_Z_ee
  	  
      -> make ee_Z_ee (compile, ee_Z_ee executable should appear)
  	  
      -> ./ee_Z_ee > ee_Z_ee.log (run, ee_Z_ee.log &
         ee_Z_ee_crossx.txt should appear)
  	  
      -> root -l plot_crossx.C'("ee_Z_ee_crossx.txt")' (plot)
  
  *** Please ensure that $PYTHIA8/bin, $PYTHIA8/include,
      $PYTHIA8/lib and $PYTHIA8/lib/libpythia8.so are 
      properly exported to the environment. Check out the Makefile 
      for this, you can modify it if needed in the python file
      "generate_pythia8_macros.py" (or directly). Once you have
      set up the Makefile in the python generator it will auto-
      matically create the right Makefile for each new folder
      created.
	  
  *** The default example is e- e+ -> Z (s-channel) -> e- e+ with
      5k events and the center of mass energy range 20 - 240 GeV
________________________________________________________________
  *** Customize the script for any process:
  
      -> You may generate whatever .cmnd files you desire to
         visualize the crossx as a function of eCM.
		 
  *** Open the generate_pythia8_macros.py and change the options
      as follows:
  
      -> string <name>: give a name to the folder that will be
         created (the name is kept for some files)
  	  
      -> list tuple <eCM_ranges>: choose the specific intervals
         in eCM you want to investigate. From one .cmnd to the
         next, eCM is the only parameter that changes.
  	  
      -> int <Nevents>: number of events in each cmnd file
  	  
      -> string <idA, idB>: PDG codes for incoming beam particles
  	  
      -> list string <options>: append the options one by one
         in this list:
           -> necessary : hard processes
           -> optional  : parton, hadron, decay Pythia8 settings.
  	  
  *** The option part is ready. You can change manually from
      here if you want some things different like the maximum
      precision used (1 decimal in eCM) or the cross section to
      not be converted to fb (default in Pythia8 is mb).
________________________________________________________________
