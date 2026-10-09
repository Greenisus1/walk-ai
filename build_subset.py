#!/usr/bin/env python3
"""Developer-only build tool: requires numpy + pyarrow, not needed to run the app."""
import argparse, csv, hashlib, json, collections, zlib
import numpy as np
import pyarrow.feather as feather


def file_hash(path, algorithm):
    h=hashlib.new(algorithm)
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def build(conn, annotations, out):
    meta = {int(r['root_id']): r for r in csv.DictReader(open(annotations), delimiter='\t')}
    import pyarrow as pa
    source = pa.ipc.open_file(pa.memory_map(conn, 'r'))
    def scan(from_ids, to_ids=None):
        sums=collections.defaultdict(int)
        for j in range(source.num_record_batches):
            batch=source.get_batch(j)
            pre=batch.column(batch.schema.get_field_index('pre_pt_root_id')).to_numpy()
            post=batch.column(batch.schema.get_field_index('post_pt_root_id')).to_numpy()
            count=batch.column(batch.schema.get_field_index('syn_count')).to_numpy()
            mask=np.isin(pre,list(from_ids))
            if to_ids is not None: mask &= np.isin(post,list(to_ids))
            for a,b,w in zip(pre[mask],post[mask],count[mask]):
                sums[(int(a),int(b))]+=int(w)
        return {pair:w for pair,w in sums.items() if w>=5}
    pools = {}
    for modality in ['sugar', 'water', 'bitter', 'grooming', 'olfactory']:
        candidates = sorted(k for k,r in meta.items() if r['super_class']=='sensory' and
                            (r['cell_sub_class']==modality or r['cell_class']==modality))
        # Evenly spaced ID sample for broad olfactory coverage, not a biological selection.
        if len(candidates)>192:
            candidates=[candidates[i*len(candidates)//192] for i in range(192)]
        pools[modality]=candidates
    if any(not p for p in pools.values()):
        raise ValueError('Required real sensory annotation pool is missing')
    selected=set(sum(pools.values(), [])); frontier=selected.copy()
    layers=[]
    # Four bounded forward layers, favouring strong anatomical connectivity.
    for _ in range(4):
        scores=collections.Counter()
        for (a,p),w in scan(frontier).items():
            if p in meta and p not in selected: scores[p]+=w
        frontier=set(k for k,_ in scores.most_common(1500))
        layers.append(len(frontier)); selected.update(frontier)
    ids=sorted(selected); idx={k:i for i,k in enumerate(ids)}
    edges=[]
    for (a,b),w in scan(selected,selected).items():
        edges.append([idx[a],idx[b],w])
    edges.sort()
    neurons=[]
    for k in ids:
        r=meta[k]
        neurons.append({'id':str(k),'type':r['cell_type'] or r['cell_class'] or r['super_class'],
                        'super_class':r['super_class'],'sub_class':r['cell_sub_class'],
                        'side':r['side'],'nt':r['top_nt']})
    obj={'neurons':neurons,'edges':edges,'inputs':{k:[idx[x] for x in v] for k,v in pools.items()},
         'provenance':{'dataset':'FlyWire FAFB v783, original Buhmann synapses',
             'connections_url':'https://zenodo.org/api/records/10676866/files/proofread_connections_783.feather/content',
             'connections_md5':file_hash(conn, 'md5'),
             'annotations_url':'https://raw.githubusercontent.com/flyconnectome/flywire_annotations/main/supplemental_files/Supplemental_file1_neuron_annotations.tsv',
             'annotations_sha256':hashlib.sha256(open(annotations,'rb').read()).hexdigest(),
             'selection':'sensory pools + four forward layers of top 1500 novel partners by summed synapses; induced edges >=5 synapses after neuropil aggregation',
             'layer_sizes':layers,'threshold':5}}
    raw=json.dumps(obj,separators=(',',':')).encode(); packed=zlib.compress(raw,9)
    open(out,'wb').write(packed)
    print('nodes',len(ids),'edges',len(edges),'compressed bytes',len(packed))
    print('inputs', {k:len(v) for k,v in pools.items()})
    print('outputs',collections.Counter(r['sub_class'] or r['super_class'] for r in neurons if r['super_class'] in ['motor','descending']))
    return obj

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('connections');p.add_argument('annotations');p.add_argument('output')
    a=p.parse_args();build(a.connections,a.annotations,a.output)
