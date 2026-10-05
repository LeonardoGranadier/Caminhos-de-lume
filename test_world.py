import sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'.deps'))
import tempfile
import unittest
from world import World,MAPS
from routes import arrive,close_dialog,route_object,JOURNEY

class WorldTests(unittest.TestCase):
    def test_full_quest_reachable_and_completable(self):
        w=World()
        for name in JOURNEY:
            arrive(w,name);w.interact();close_dialog(w)
        self.assertTrue(w.completed);self.assertEqual(w.fragments,3)
        self.assertEqual(w.visited,set(MAPS));self.assertTrue(w.key)
        self.assertEqual(w.gold,100)

    def test_chests_cannot_be_farmed(self):
        w=World();arrive(w,'vila_fragmento');w.interact();close_dialog(w)
        w.interact();close_dialog(w);self.assertEqual(w.fragments,1)
        arrive(w,'vila_moedas');w.interact();close_dialog(w);w.interact()
        self.assertEqual(w.gold,30)

    def test_locked_gate(self):
        w=World();arrive(w,'saida_bosque')
        route=route_object(w,'entrada_ruinas')
        for x,y in route[:-1]:self.assertTrue(w.move(x-w.x,y-w.y))
        x,y=route[-1];self.assertFalse(w.move(x-w.x,y-w.y))
        self.assertEqual(w.area,'bosque');self.assertTrue(w.dialog)

    def test_npcs_and_terrain_block_movement(self):
        w=World();arrive(w,'Iara')
        self.assertFalse(w.move(*w.facing))
        self.assertFalse(w.current.walkable(0,0));self.assertFalse(w.current.walkable(-1,0))
        w.interact();pos=(w.x,w.y);self.assertFalse(w.move(0,1));self.assertEqual(pos,(w.x,w.y))

    def test_save_roundtrip_and_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'save.json';w=World(p)
            for name in JOURNEY[:5]:arrive(w,name);w.interact();close_dialog(w)
            w.save();loaded=World(p);self.assertTrue(loaded.load())
            self.assertEqual((loaded.area,loaded.x,loaded.y,loaded.fragments,loaded.opened,loaded.key),(w.area,w.x,w.y,w.fragments,w.opened,w.key))
            p.write_text('broken');self.assertFalse(loaded.load());self.assertEqual(loaded.fragments,1)

    def test_every_interactable_has_a_path(self):
        w=World();spawns={'vila':(16,15),'bosque':(3,15),'ruinas':(3,18)}
        for name,area in w.areas.items():
            w.area=name;w.x,w.y=spawns[name]
            for o in area.objects:route_object(w,o['id'])

    def test_final_reward_is_one_time(self):
        w=World()
        for name in JOURNEY:arrive(w,name);w.interact();close_dialog(w)
        w.interact();close_dialog(w);self.assertEqual(w.gold,100)

if __name__=='__main__':unittest.main(verbosity=2)
