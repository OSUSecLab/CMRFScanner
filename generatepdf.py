
from pdg_js.build_pdg import get_data_flow
import pdg_js.display_graph as display_graph
dfg_nodes=get_data_flow("try.js",{})
display_graph.draw_pdg(dfg_nodes, attributes=True,save_path="try.pdf")