# coding: utf-8
import mock
import uuid
import traceback

from django.core.management.base import BaseCommand

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.balance import formulas as f

from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage

from game.map.roads.storage import waymarks_storage


class Command(BaseCommand):

    help = 'test how hero move in levels corridor on real map'

    requires_model_validation = False

    option_list = BaseCommand.option_list

    @mock.patch('game.balance.constants.EXP_PER_QUEST_FRACTION', 0.0)
    def handle(self, *args, **options):
        try:
            self.test_corridor()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()


    def test_corridor(self):

        result, account_id, bundle_id = register_user(uuid.uuid4().hex) # pylint: disable=W0612
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        current_time = TimePrototype.get_current_time()

        old_level = 0

        for level in xrange(1, 100):
            print 'process level %d\texpected turns: %d' % (level, f.turns_on_lvl(level))

            if old_level != self.hero.level:
                self.hero.abilities.randomized_level_up(self.hero.level - old_level)
                old_level = self.hero.level

            for i in xrange(f.turns_on_lvl(level)): # pylint: disable=W0612
                self.storage.process_turn()
                current_time.increment_turn()

            exp_to_next_level = float(self.hero.experience) / f.exp_on_lvl(self.hero.level) * 100
            exp_from_expected = float(f.total_exp_to_lvl(self.hero.level)+self.hero.experience)/f.total_exp_to_lvl(level+1)*100
            exp_untaken = f.total_exp_to_lvl(level+1) - f.total_exp_to_lvl(self.hero.level) - self.hero.experience
            quests_untaken = float(exp_untaken) / f.experience_for_quest(waymarks_storage.average_path_length)
            print u'hero level: %d\texp: %.2f%%\texp from expected: %.2f%% (%d exp, %.2f quests)\ttotal quests %d' % (self.hero.level,
                                                                                                                      exp_to_next_level,
                                                                                                                      exp_from_expected,
                                                                                                                      exp_untaken,
                                                                                                                      quests_untaken,
                                                                                                                      self.hero.statistics.quests_done)
