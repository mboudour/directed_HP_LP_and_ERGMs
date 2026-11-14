# ruff: noqa: E501
"""NHP-D (NHP-D-mean and NHP-D-maxmin+) for singleton-tail directed hypergraphs.

The model class, training loop and scoring are taken unchanged from the author's NHP-D script
for temporal directed F-hypergraphs (08_named_nhpd_node2vec_temporal_farc_completion.py). The
node features are Node2Vec embeddings of the clique expansion of the training hyperarcs with
p = q = 1 (uniform random walks), 64 dimensions, 10 walks of length 20 per node, window 5 and
5 epochs, as in that script; the walks are generated here and embedded with gensim's Word2Vec,
because the node2vec package requires an older NumPy than the rest of the code.
"""

import random

import numpy as np
import scipy.sparse as sp
import torch
from gensim.models import Word2Vec
from torch import nn

SEED = 20260817


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def clique_adjacency(arcs, n):
    """arcs: list of (tail, head tuple). Returns normalized sparse adjacency with self-loops and neighbour lists."""
    rows, cols = [], []
    nbr = [set() for _ in range(n)]
    for t, H in arcs:
        members = [t, *H]
        for a, u in enumerate(members):
            for v in members[a + 1:]:
                rows += [u, v]
                cols += [v, u]
                nbr[u].add(v)
                nbr[v].add(u)
    rows += list(range(n))
    cols += list(range(n))
    M = sp.coo_matrix((np.ones(len(rows), np.float32), (rows, cols)), shape=(n, n)).tocsr()
    deg = np.asarray(M.sum(1)).ravel()
    inv = np.power(np.maximum(deg, 1), -0.5)
    N = (sp.diags(inv) @ M @ sp.diags(inv)).tocoo()
    adj = torch.sparse_coo_tensor(torch.tensor(np.vstack([N.row, N.col]), dtype=torch.long), torch.tensor(N.data, dtype=torch.float32), size=N.shape).coalesce()
    return adj, [sorted(s) for s in nbr]


def node2vec_features(nbr, n, dim=64, walk_length=20, num_walks=10, seed=SEED):
    rng = random.Random(seed)
    nodes = [i for i in range(n) if nbr[i]]
    X = np.zeros((n, dim), np.float32)
    if len(nodes) < 4:
        return torch.tensor(X)
    walks = []
    for _ in range(num_walks):
        order = nodes[:]
        rng.shuffle(order)
        for v in order:
            w = [v]
            while len(w) < walk_length:
                w.append(rng.choice(nbr[w[-1]]))
            walks.append([str(x) for x in w])
    model = Word2Vec(walks, vector_size=dim, window=5, min_count=1, sg=1, workers=1, seed=seed, epochs=5, batch_words=64)
    for v in nodes:
        X[v] = model.wv[str(v)]
    return torch.tensor(X)


def tensorize(rows):
    """rows: list of (tail, head tuple, label)."""
    length = max(len(h) for _, h, _ in rows)
    head = torch.zeros((len(rows), length), dtype=torch.long)
    mask = torch.zeros((len(rows), length), dtype=torch.float32)
    for r, (_, h, _) in enumerate(rows):
        head[r, : len(h)] = torch.tensor(h)
        mask[r, : len(h)] = 1
    return torch.tensor([t for t, _, _ in rows], dtype=torch.long), head, mask, torch.tensor([y for _, _, y in rows], dtype=torch.float32)


class NHPD(nn.Module):
    """NHP-D-mean or NHP-D-maxmin+ with a hyperlink-aware GCN and direction loss (unchanged)."""

    def __init__(self, dim, variant):
        super().__init__()
        self.variant = variant
        self.global_layer = nn.Linear(dim, dim)
        self.local_self = nn.Linear(dim, dim, bias=False)
        self.local_neighbour = nn.Linear(dim, dim)
        self.interaction = nn.Linear(dim, 1)
        self.direction = nn.Parameter(torch.empty(dim, dim))
        self.direction_bias = nn.Parameter(torch.zeros(1))
        nn.init.xavier_uniform_(self.direction)

    def encode(self, x, adjacency):
        return torch.nn.functional.normalize(torch.relu(self.global_layer(torch.sparse.mm(adjacency, x))), p=2, dim=1)

    def forward(self, node, tail, head, mask):
        t = node[tail]
        h = node[head]
        n = mask.sum(dim=1, keepdim=True).clamp(min=1)
        hsum = (h * mask.unsqueeze(-1)).sum(dim=1)
        tl = torch.relu(self.local_self(t) + self.local_neighbour(hsum / n))
        h_neigh = (hsum.unsqueeze(1) + t.unsqueeze(1) - h) / n.unsqueeze(-1)
        hl = torch.relu(self.local_self(h) + self.local_neighbour(h_neigh))
        if self.variant == "mean":
            interaction = 0.5 * (tl + (hl * mask.unsqueeze(-1)).sum(dim=1) / n)
        else:
            minimum = hl.masked_fill(mask.unsqueeze(-1) == 0, float("inf")).min(dim=1).values
            interaction = torch.relu(tl - minimum)
        hyperlink = self.interaction(interaction).squeeze(-1)
        hmean = (hl * mask.unsqueeze(-1)).sum(dim=1) / n
        direction = torch.einsum("bi,ij,bj->b", tl, self.direction, hmean) + self.direction_bias
        return hyperlink, direction


def train(model, feature, adjacency, train_data, valid_data, epochs=100):
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    pos = float(train_data[3].sum())
    neg = len(train_data[3]) - pos
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([neg / max(pos, 1.0)]))
    best, best_loss, stale = None, float("inf"), 0
    for _ in range(epochs):
        model.train()
        permutation = torch.randperm(len(train_data[3]))
        for begin in range(0, len(permutation), 256):
            ix = permutation[begin: begin + 256]
            node = model.encode(feature, adjacency)
            hyper, direct = model(node, *(tensor[ix] for tensor in train_data[:3]))
            label = train_data[3][ix]
            loss = loss_fn(hyper, label) + 0.25 * loss_fn(direct, label)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            node = model.encode(feature, adjacency)
            hyper, direct = model(node, *valid_data[:3])
            value = float((loss_fn(hyper, valid_data[3]) + 0.25 * loss_fn(direct, valid_data[3])).item())
        if value < best_loss - 1e-5:
            best_loss = value
            best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= 15:
                break
    model.load_state_dict(best)
    return best_loss


def scores(model, feature, adjacency, data):
    model.eval()
    with torch.no_grad():
        node = model.encode(feature, adjacency)
        hyper, direct = model(node, *data[:3])
        return torch.sigmoid(hyper + 0.25 * direct).numpy()
