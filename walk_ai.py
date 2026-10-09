#!/usr/bin/env python3
"""Walk AI: real FlyWire wiring, deliberately unserious chat interface. Python 3.9+."""
import argparse
import base64
import bisect
import collections
import json
import random
import re
import zlib
from pathlib import Path

# Data attribution: FlyWire Consortium / Dorkenwald et al. (Nature 2024),
# doi:10.1038/s41586-024-07558-y; Schlegel et al., doi:10.1038/s41586-024-07686-5.
# Buhmann synapse detection, Heinrich clefts, Eckstein/Bates NT predictions.
# Dataset license: CC BY 4.0, https://zenodo.org/records/10676866
# Annotations: https://github.com/flyconnectome/flywire_annotations/tree/main
# Modified by summing neuropils, retaining edges >=5 synapses, and sensory-rooted subsetting.
# This is a comic random-walk interface, not a validated brain/behavior model.
# The release builder embeds the compressed, attributed real-data subset here.
VERSION = '1.1.0'

DATA_FILES = ['brain_1.b85', 'brain_2.b85', 'brain_3.b85', 'brain_4.b85', 'brain_5.b85', 'brain_6.b85']
DATA_SHA256 = '9fd1a7e75b7c42c47b72d184e488a117bc9d1b931ac168bee63ff5571d3ef4b2'


def obtain_data():
    import urllib.request, hashlib
    folder=Path(__file__).resolve().parent / 'walk_ai_data'
    cache=folder / 'brain.zlib'
    if cache.exists():
        packed=cache.read_bytes()
        if hashlib.sha256(packed).hexdigest()==DATA_SHA256: return packed
        raise ValueError('Cached brain checksum failed; remove walk_ai_data/brain.zlib and retry')
    folder.mkdir(exist_ok=True)
    pieces=[]
    print('Downloading real fly wiring once. Later runs work offline.')
    for name in DATA_FILES:
        # GitHub public repository content API supplies the exact download URL.
        api='https://api.github.com/repos/Greenisus1/walk-ai/contents/'+name+'?ref=main'
        with urllib.request.urlopen(api,timeout=60) as response:
            entry=json.load(response)
        url=entry.get('download_url')
        if not url: raise ValueError('Missing GitHub download URL for '+name)
        with urllib.request.urlopen(url,timeout=60) as response:
            pieces.append(response.read().decode('ascii').strip())
        print('  '+name+' downloaded')
    packed=base64.b85decode(''.join(pieces))
    if hashlib.sha256(packed).hexdigest()!=DATA_SHA256:
        raise ValueError('Downloaded brain checksum failed; refusing to run')
    temp=folder / 'brain.zlib.tmp'
    temp.write_bytes(packed);temp.replace(cache)
    return packed


LEXICON = {
    'sugar': {'sugar', 'sweet', 'cake', 'banana', 'fruit', 'food', 'eat', 'hungry', 'candy'},
    'water': {'water', 'drink', 'thirsty', 'rain', 'wet'},
    'bitter': {'bitter', 'poison', 'toxic', 'coffee', 'bad', 'gross'},
    'grooming': {'dust', 'dirty', 'itch', 'scratch', 'groom', 'clean', 'antenna', 'touch'},
    'olfactory': {'smell', 'scent', 'hello', 'hi', 'hey', 'stink', 'perfume'},
}
REPLIES = {
    'eat': ['i have assessed your argument and chosen to lick it.', 'banana? banana.'],
    'sip': ['tiny mouth deployed. conversation hydrated.', 'i extend my proboscis. this is my entire opinion.'],
    'groom': ['hold on. washing my face with my legs.', 'antenna maintenance. your meeting has been postponed.'],
    'turn left': ['i turn left. devastating rebuttal.', 'left. that is all the processing you get.'],
    'turn right': ['i turn right and consider this problem solved.', 'right turn. no further questions.'],
    'wander': ['i walk away from this conversation in six-legged confidence.', 'have you considered wandering aimlessly?'],
    'quiet': ['no motor readout reached. i am staring at the wall.', 'brain traffic. please wait approximately one fly eternity.'],
}


def load_data(path=None):
    packed=Path(path).read_bytes() if path else obtain_data()
    obj=json.loads(zlib.decompress(packed))
    if not obj['edges'] or not obj['neurons']:
        raise ValueError('No real connectome data; refusing to substitute a fake brain')
    return obj


class Scene:
    """Handwritten world/reflex layer. Never presented as connectome intelligence."""
    def __init__(self):
        self.alive=True
        self.last_behavior=None
        self.lines={}

    def react(self,text):
        t=text.lower()
        words=set(re.findall(r'[a-z]+',t))
        if words & {'revive','respawn','restart','reset'}:
            self.alive=True
            return 'revive'
        death = bool(words & {'dead','die','died','death','killed'})
        if 'not dead' in t or 'not die' in t or "don't die" in t: death=False
        if death:
            self.alive=False
            return 'dead'
        if not self.alive: return 'dead'
        if words & {'rock','rocks','car','cars','truck','swatter','danger','hazard','hazards','obstacle','obstacles','crush','wall'}:
            directions=set()
            for k,v in [('left',{'left'}),('right',{'right'}),('up',{'up','above','overhead'}),('down',{'down','below'}),('front',{'front','ahead'}),('back',{'back','behind'})]:
                if words & v: directions.add(k)
            if len(directions)>=4 or 'all sides' in t or 'surrounded' in t:
                return 'trapped'
            if 'left' in directions and 'right' not in directions: return 'dodge right'
            if 'right' in directions and 'left' not in directions: return 'dodge left'
            if 'front' in directions and 'back' not in directions: return 'retreat'
            return 'escape'
        if words & {'heat','hot','burning','fire','sun','sunlight'}: return 'shade'
        if words & {'light','bright','lamp'}: return 'inspect light'
        if words & {'water','drink','thirsty','wet'}: return 'sip'
        if words & {'bitter','poison','toxic','gross'}: return 'reject'
        if words & {'food','banana','fruit','sugar','sweet','cake','hungry','eat','candy'}: return 'eat'
        if words & {'dust','dusty','dirty','itch','scratch','groom','clean','antenna'}: return 'groom'
        return None

    def line(self,behavior,rng):
        options=REPLIES[behavior]
        # Never repeat a behavior's previous line on its next occurrence.
        available=[x for x in options if x!=self.lines.get(behavior)] or options
        line=rng.choice(available);self.lines[behavior]=line
        self.last_behavior=behavior
        return line


REPLIES.update({
    'dead': ['i am dead. no more turns. tiny funeral please.',
             'still dead. type /revive if you want another round.',
             'six legs, zero pulse. this fly is no longer taking requests.'],
    'revive': ['respawned. terrible decisions are available again.',
               'alive again. somebody rebooted the raisin with wings.'],
    'trapped': ['rocks on every side? no clear escape route. i freeze and brace.',
                'that is a rock sandwich and i am the filling. no safe dodge found.',
                'too many blocked directions. i stop instead of inventing a safe turn.'],
    'dodge right': ['rock from the left. dodging right before i become fly paste.',
                    'left side is dangerous. moving right, assuming that side is clear.'],
    'dodge left': ['danger on the right. dodging left.',
                   'right side blocked. left looks like the less terrible option.'],
    'retreat': ['obstacle ahead. backing off, assuming behind me is clear.',
                'front is blocked. reverse the tiny vehicle.'],
    'escape': ['hazard detected. i back away and look for an open route.',
               'something wants to flatten me. leaving the danger zone, route unknown.'],
    'shade': ['too hot. heading for shade instead of cooking my one brain cell.',
              'sun detected. seeking a cooler spot. i am not a solar panel.',
              'heat is bad for the tiny pilot. shade break.'],
    'inspect light': ['light source detected. i inspect it from a cautious distance.',
                      'bright thing. curious, but i am not promising it is safe to approach.'],
    'reject': ['bitter or toxic? rejecting it. i would like to remain a fly.',
               'no licking the suspicious substance. survival first.'],
})
REPLIES['sip']=['water. landing nearby and taking a tiny sip.',
                'hydration located. proboscis out, not a random right turn.',
                'drink break. one microscopic slurp, please.']
REPLIES['eat']=['food spotted. inspect, land, then lick. a serious business plan.',
                'banana? finally, a question my mouth can answer.',
                'snack time. approaching the food instead of orbiting the conversation.']


class Brain:
    def __init__(self, obj, seed=None):
        self.obj=obj; self.neurons=obj['neurons']; self.rng=random.Random(seed)
        self.adj=[[] for _ in self.neurons]; self.cumulative=[[] for _ in self.neurons]
        for pre,post,count in obj['edges']:
            self.adj[pre].append(post)
            c=self.cumulative[pre]; c.append((c[-1] if c else 0)+count)
        self.memory=collections.Counter(); self.scene=Scene()

    def stimulus(self, text):
        words=set(re.findall(r'[a-z]+',text.lower()))
        scored={k:len(words & v) for k,v in LEXICON.items()}
        chosen=[k for k,s in scored.items() if s]
        # English not recognised: a generic arbitrary odour, never a language model.
        if not chosen: chosen=['olfactory']
        return chosen

    def run(self, text, walkers=768, hops=16):
        reflex=self.scene.react(text)
        if reflex=='dead':
            self.memory.clear()
            return {'behavior':'dead','reply':self.scene.line('dead',self.rng),
                    'modalities':[],'hits':0,'active':0,'winner':None,'path':[],
                    'decision_source':'handwritten world state','graph_behavior':'inactive', 'alive':False}
        modes=self.stimulus(text)
        inputs=[n for k in modes for n in self.obj['inputs'][k]]
        if not inputs: raise ValueError('Sensory pool is empty')
        readout=collections.Counter(); visits=collections.Counter(); example={}
        for _ in range(walkers):
            cur=self.rng.choice(inputs); path=[cur]
            for step in range(hops):
                if not self.adj[cur]: break
                weights=self.cumulative[cur]
                edge=bisect.bisect_right(weights,self.rng.randrange(weights[-1]))
                cur=self.adj[cur][edge];path.append(cur);visits[cur]+=1
                if self.neurons[cur]['super_class'] in ('motor','descending'):
                    readout[cur]+=1;example.setdefault(cur,path[:]);break
                # Activity leak: a 7% per-hop loss. No excitatory/inhibitory claim.
                if self.rng.random()<0.07: break
        # Carry weak activity between turns, not new graph edges or learned language.
        self.memory=collections.Counter({k:v*0.2 for k,v in self.memory.items() if v*0.2>=0.1})
        self.memory.update(readout)
        if not self.memory and reflex is None:
            return {'behavior':'quiet','reply':self.scene.line('quiet',self.rng),
                    'modalities':modes,'hits':0,'active':len(visits),'winner':None,'path':[]}
        winner=self.memory.most_common(1)[0][0] if self.memory else None
        neuron=self.neurons[winner] if winner is not None else None
        graph_behavior=self.behavior(neuron) if neuron else 'quiet'
        behavior=reflex or graph_behavior
        reply=self.scene.line(behavior,self.rng)
        return {'behavior':behavior,'reply':reply,
                'modalities':modes,'hits':sum(readout.values()),'active':len(visits),
                'winner':neuron,'path':[self.neurons[i]['id'] for i in example.get(winner,[])],
                'decision_source':'handwritten world reflex' if reflex else 'comic graph readout',
                'graph_behavior':graph_behavior,'alive':self.scene.alive}

    @staticmethod
    def behavior(neuron):
        # These are comic labels, NOT validated behavior predictions.
        sub=neuron['sub_class']
        if sub in ('ingestion_motor_neuron','crop_motor_neuron'): return 'eat'
        if sub in ('proboscis_motor_neuron','haustellum_motor_neuron','salivary_motor_neuron'): return 'sip'
        if sub=='antennal_motor_neuron': return 'groom'
        if neuron['super_class']=='descending' and neuron['side'] in ('left','right'):
            return 'turn '+neuron['side']
        return 'wander'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',help='optional external .zlib data; default is bundled')
    p.add_argument('--seed',type=int,help='repeatable random walks')
    p.add_argument('--once',help='one message instead of interactive chat')
    p.add_argument('--trace',action='store_true',help='print neuron IDs and real edge path')
    p.add_argument('--info',action='store_true',help='print dataset attribution and selection')
    a=p.parse_args();obj=load_data(a.data);brain=Brain(obj,a.seed)
    if a.info:
        print(json.dumps(obj['provenance'],indent=2));print('Neurons:',len(obj['neurons']),'Edges:',len(obj['edges']));return
    def reply(text):
        r=brain.run(text)
        print('walk ai> '+r['reply']+' ['+r['behavior']+']')
        if a.trace:
            print('  stimulus:',','.join(r['modalities']), '| output hits:',r['hits'],'| visited:',r['active'])
            print('  readout:',r['winner'])
            print('  decision:',r.get('decision_source','comic graph readout'), '| graph suggestion:',r.get('graph_behavior','quiet'))
            print('  real path:', ' -> '.join(r['path']) or '(no new output path this turn)')
    if a.once is not None: reply(a.once);return
    print('Walk AI / real fly wiring, fake English skills. No LLM, no internet needed.')
    print('Real graph + handwritten world reflexes. Replies are jokes, not scientific predictions.')
    print('Try: banana / water / bitter / dusty antenna / hello. /quit exits; /trace toggles paths; /revive brings the fly back.')
    try:
        while True:
            text=input('you> ').strip()
            if text.lower() in ('/quit','/exit'): break
            if text=='/revive': brain.memory.clear();reply('revive');continue
            if text=='/trace': a.trace=not a.trace;print('trace:',a.trace);continue
            if text: reply(text)
    except (EOFError,KeyboardInterrupt): print('\nfly escaped.')


if __name__=='__main__':
    main()
