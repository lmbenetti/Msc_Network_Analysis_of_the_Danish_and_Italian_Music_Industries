import torch, torch_geometric
from scipy.special import binom
from sklearn.decomposition import PCA

device = "cuda" if torch.cuda.is_available() else "cpu"

def make_tensor(G, df):
   edge_index = [[], []]
   edge_attribute_names = list(list(G.edges(data = True))[0][2].keys())
   edge_attr = []
   for edge in G.edges(data = True):
      edge_index[0].append(edge[0])
      edge_index[1].append(edge[1])
      edge_index[0].append(edge[1])
      edge_index[1].append(edge[0])
      edge_attr.append([edge[2][edge_attribute_names[i]] for i in range(len(edge_attribute_names))])
      edge_attr.append([edge[2][edge_attribute_names[i]] for i in range(len(edge_attribute_names))])
   tensor = torch_geometric.data.Data(
      edge_index = torch.tensor(edge_index, dtype = torch.long).to(device),
      node_vects = torch.tensor(df.values, dtype = torch.float).double().to(device),
      edge_attr = torch.tensor(edge_attr, dtype = torch.float).double().to(device)
   )
   return tensor

def _Linv(tensor):
   L_ei, Lew = torch_geometric.utils.get_laplacian(tensor.edge_index)
   L = torch_geometric.utils.to_dense_adj(edge_index = L_ei, edge_attr = Lew)[0]
   return torch.linalg.pinv(L, hermitian = True).double()

def _er(tensor, Linv):
   if Linv is None:
      Linv = _Linv(tensor)
   pinv_diagonal = torch.diagonal(Linv)
   return pinv_diagonal.unsqueeze(0) +  pinv_diagonal.unsqueeze(1) - 2 * Linv

def _pairwise_distances(tensor, Linv):
   if Linv is None:
      Linv = _Linv(tensor)
   distances = torch.zeros((tensor.node_vects.shape[1], tensor.node_vects.shape[1])).to(device)
   for i in range(tensor.node_vects.shape[1]):
      diff = tensor.node_vects[:,i] - tensor.node_vects[:,i + 1:].T
      distances[i,i + 1:] = (diff * torch.mm(Linv, diff.T).T).sum(dim = 1)
   #TODO: Forgot square root here?
   return distances

def ge(src, trg, Linv = None):
   diff = src - trg
   return torch.sqrt((diff * torch.matmul(Linv, diff)).sum())

