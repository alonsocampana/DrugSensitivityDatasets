from torch.utils.data import Dataset
import torch
from torch_geometric.data import Batch

class TorchGraphsDataset(Dataset):
    def __init__(self, data, drug_dict, line_dict, filter_missing = True):
        self.data = data
        self.drug_dict = drug_dict
        self.line_dict = line_dict
        if filter_missing:
            drugs = list(self.drug_dict.keys())
            lines = list(self.line_dict.keys())
        self.data = self.data.query("DRUG_ID in @drugs & CELL_ID in @lines")
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        entry = self.data.iloc[idx]
        drug = entry.loc["DRUG_ID"]
        line = entry.loc["CELL_ID"]
        drug_graph  = self.drug_dict[drug].clone()
        drug_graph["y"] = torch.Tensor([entry["Y"]])
        drug_graph["cell"] = self.line_dict[line].clone()
        return drug_graph

class TorchGraphsDrugwiseDataset(Dataset):
    def __init__(self, data, drug_dict, line_dict, filter_missing = True):
        self.data = data
        self.drug_dict = drug_dict
        self.line_dict = line_dict
        if filter_missing:
            drugs = list(self.drug_dict.keys())
            lines = list(self.line_dict.keys())
        self.data = self.data.query("DRUG_ID in @drugs & CELL_ID in @lines")
        self.drugs = self.data.loc[:, "DRUG_ID"].unique()
    def __len__(self):
        return len(self.drugs)
    def __getitem__(self, idx):
        drug = self.drugs[idx]
        drug_graph  = self.drug_dict[drug].clone()
        entries = self.data.query("DRUG_ID == @drug")
        y = entries.loc[:, ["Y"]].to_numpy()
        drug_graph["y"] = torch.Tensor(y)
        lines = list(entries.loc[:, ["CELL_ID"]].to_numpy().squeeze())
        drug_graph["cell"] = torch.stack([self.line_dict[lines[i]].clone() for i in range(len(lines))])
        return drug_graph

class TorchGraphsCellwiseDataset(Dataset):
    def __init__(self, data, drug_dict, line_dict, filter_missing = True):
        self.data = data
        self.drug_dict = drug_dict
        self.line_dict = line_dict
        if filter_missing:
            drugs = list(self.drug_dict.keys())
            lines = list(self.line_dict.keys())
        self.data = self.data.query("DRUG_ID in @drugs & CELL_ID in @lines")
        self.lines = self.data.loc[:, "CELL_ID"].unique()
    def __len__(self):
        return len(self.lines)
    def __getitem__(self, idx):
        line = self.lines[idx]
        entries = self.data.query("CELL_ID == @line")
        y = entries.loc[:, ["Y"]].to_numpy()
        drugs = entries.loc[:, ["DRUG_ID"]]
        drug_graph  = Batch.from_data_list([self.drug_dict[drug].clone() for drug in list(drugs.to_numpy().squeeze())])
        drug_graph["y"] = torch.Tensor(y)
        drug_graph["cell"] = self.line_dict[line]
        return drug_graph