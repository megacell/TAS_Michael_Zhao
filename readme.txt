 This folder contains algorithms to solve the traffic assignment problem in the static case.
 The User Equilibrium and Social Optimum can be computed for homogeneous or heterogeneous games thanks to different versions of the Frank-Wolfe algorithm, including the upgraded of Fukushima's algorithm.
 Demand_Study.py is the most basic runnnable file. Input a demand ratio, a network, and a mode. It will take data from the data folder for this network, compute the flow for this mode and this demand thanks to the implementation of the homogeneous Fukushima's algorithm, and output a csv file containing flows for every edge of the network in the data/output folder.
 The other Dem_.py files do approximately the same, check the code to know which arguments to input and what it will output
 Some additional files plot graph that can be useful to show your results


Here is a more detailed description of the structure of the folder:

>data -- Contains all the network data
 >Paths -- Contains the links for the paths used in the TRB paper
 -Name_net.csv -- Links of the network : link ID, origin and destination, cost funstion as a0 to a4
 -Name_net.txt -- Some more information on the links, like capacity, length, free-flow travel time...
 -Name_od.csv -- Origin-Destination pairs : Origin, Destination, and volume
 -Name_node.csv -- Coordinates of the nodes in the network
 >output -- Folder in which each algorithm writes its results
>visualization -- folder for visualization of the flow. Does not work on every network, and only for the homogeneous game. It's a good tool to check that your results are coherent
 -geojson_features_anything -- Data that can be visualized, create your own !
 -geojson_features.js -- data that will be considered by view_network. Change the name of your file to this so that it gets considered
 -view_network.html -- double click and view the geojson_features.js network
>tests -- some test functions to test if the algorithms are working correctly. Modify them to test your functions
-frank_wolfe_... -- the frank-wolfe/fukushima solvers are implemented in these files. Currently, the best ones are solver_3 for the homogeneous solver, and fw_heterogeneous_1 for the heterogeneous one
-Demand_Study.../Dem... -- Files that you can directly run. They will write the results you need in the data/output folder
-Speed_Utils/process_data/utils... -- Utilitary functions
-traveltimes/Toy_.../... -- Some files for plotting graphs that were used in previous articles
  

Each python file has an __author__ line for credits, an __email__ line for questions, and a comment which describes the structure and use of the file.
For any questions about a particular file, please email the authors. For more general questions, please email the first author of the concerned files. for questions about this readme, please email signargout@berkeley.edu
