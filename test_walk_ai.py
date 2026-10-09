#!/usr/bin/env python3
"""Checks bundled real-data identity and actual path traversal, without network."""
import collections, hashlib, resource, time, unittest
import walk_ai

class TestFly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=walk_ai.load_data()
        cls.edge_ids={(cls.obj['neurons'][a]['id'], cls.obj['neurons'][b]['id']) for a,b,w in cls.obj['edges']}

    def test_release(self):
        self.assertEqual(self.obj['provenance']['connections_md5'],'f48f972d262323a102aed49af1396b8a')
        self.assertEqual(len(self.obj['neurons']),5589)
        self.assertEqual(len(self.obj['edges']),199165)
        self.assertTrue(all(w>=5 for a,b,w in self.obj['edges']))

    def test_inputs_are_real_sensory(self):
        for pool in self.obj['inputs'].values():
            self.assertTrue(pool)
            self.assertTrue(all(self.obj['neurons'][i]['super_class']=='sensory' for i in pool))

    def test_paths_follow_real_edges(self):
        winners=set()
        for message in ('banana','water','bitter','dusty antenna','hello','quantum physics'):
            b=walk_ai.Brain(self.obj,7)
            r=b.run(message)
            self.assertGreater(r['hits'],0)
            self.assertIn(r['winner']['super_class'], ('motor','descending'))
            self.assertTrue(all(pair in self.edge_ids for pair in zip(r['path'],r['path'][1:])))
            winners.add(r['winner']['id'])
        self.assertGreater(len(winners),1)

    def test_seed_and_no_output(self):
        self.assertEqual(walk_ai.Brain(self.obj,9).run('banana'),walk_ai.Brain(self.obj,9).run('banana'))
        blank={'neurons':self.obj['neurons'],'inputs':self.obj['inputs'],'edges':[]}
        r=walk_ai.Brain(blank,7).run('quantum physics')
        self.assertEqual(r['behavior'],'quiet')
        self.assertIsNone(r['winner'])

    def test_keyword_boundaries(self):
        b=walk_ai.Brain(self.obj,7)
        self.assertEqual(b.stimulus('whiCH'),['olfactory'])
        self.assertEqual(b.stimulus('sugar water'),['sugar','water'])

    def test_world_cases(self):
        cases={'water':'sip','food':'eat','sun':'shade','light':'inspect light','heat':'shade',
               'rock from left':'dodge right','rock from right':'dodge left',
               'rock coming from left, right up, and down, and in front of you':'trapped',
               'poison food':'reject','dusty antenna':'groom'}
        for text,expected in cases.items():
            with self.subTest(text=text):
                r=walk_ai.Brain(self.obj,7).run(text)
                self.assertEqual(r['behavior'],expected)
                self.assertEqual(r['decision_source'],'handwritten world reflex')
                self.assertTrue(all(pair in self.edge_ids for pair in zip(r['path'],r['path'][1:])))

    def test_death_persists_and_revives(self):
        b=walk_ai.Brain(self.obj,7)
        for text in ('you die','food','sun','water','dead'):
            r=b.run(text)
            self.assertEqual(r['behavior'],'dead')
            self.assertFalse(r['alive'])
            self.assertEqual(r['hits'],0)
            self.assertEqual(r['path'],[])
        self.assertEqual(b.run('/revive')['behavior'],'revive')
        self.assertEqual(b.run('food')['behavior'],'eat')

    def test_no_immediate_repeated_line(self):
        b=walk_ai.Brain(self.obj,7)
        lines=[b.run('water')['reply'] for _ in range(12)]
        self.assertTrue(all(a!=b for a,b in zip(lines,lines[1:])))
        self.assertGreaterEqual(len(set(lines)),3)

    def test_negated_death(self):
        b=walk_ai.Brain(self.obj,7)
        self.assertTrue(b.run('not dead')['alive'])

if __name__=='__main__':
    start=time.perf_counter();result=unittest.main(exit=False)
    print('Suite seconds:',round(time.perf_counter()-start,3))
    print('Peak RSS KiB (includes test edge-ID set):',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    if not result.result.wasSuccessful(): raise SystemExit(1)
