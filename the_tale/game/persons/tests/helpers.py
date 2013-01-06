# coding: utf-8

import random

from game import names

from game.game_info import GENDER
from game.balance.enums import RACE, PERSON_TYPE

from game.persons.prototypes import PersonPrototype

def create_person(place, state):
    race = random.choice(RACE._CHOICES)[0]
    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))
    return PersonPrototype.create(place,
                                  state=state,
                                  race=race,
                                  tp=random.choice(PERSON_TYPE._ALL),
                                  name=names.generator.get_name(race, gender),
                                  gender=gender)
