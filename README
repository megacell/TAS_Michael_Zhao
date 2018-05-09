# TA Code Documentation
## Major Changes I Made
* Modified `frank_wolfe_2.py`, `AoN_igraph.py`, and `frank_wolfe_heterogeneous.py` to record, update, and return path flows
* The end of `frank_wolfe_heterogeneous.py` or the script `run_cog_cost.py` shows how I run the cognitive cost model:
	* Iterate over the app (routed) user percentage (alpha) from 0-100%
	* Load LA_net input files
	* Modify two links to increase capacity
	* Set threshold (1000) so that links under that capacity have increased cognitive cost (3000x) for non app (non routed) users
	* Using 50% demand and modify to maintain 4000 veh/hr units of flow
	* Get graph with adjusted cognitive costs for non app users
	* Split demand based on alpha
	* Run frank-wolfe algorithm (every iteration I also do a sanity check to make sure path flows and link flows add up)
	* Output link flows, path flows, and nash distance
* `frank_wolfe_heterogeneous2.py` is my implementation of the restricted path choice model
* `graph_results.py` is a script that
	* Compiles OD data from frank-wolfe output into a single file for one OD pair (all paths for that OD pair at all app usage percentages in decreasing path flow order)
	* Calculates nash distance if necessary (old versions of `frank_wolfe_heterogeneous.py` didn't do that)
	* Produces OD data used in static model dashboard
	* Graphs path flow and travel times against app usage percentage for app users and non app users
* `convert_for_dash.py` makes all files necessary for dashboard (including the OD data that the last script can also create)