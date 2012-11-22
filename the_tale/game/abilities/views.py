# coding: utf-8

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.heroes.prototypes import HeroPrototype

from game.abilities.deck import ABILITIES

class AbilitiesResource(Resource):

    @login_required
    def initialize(self, ability_type=None, *argv, **kwargs):
        super(AbilitiesResource, self).initialize(*argv, **kwargs)
        self.ability_type = ability_type

        if self.ability is None:
            raise Error('abilities.wrong_ability', u'У вас нет такой способности')

        if self.ability.on_cooldown(self.time, HeroPrototype.get_by_account_id(self.account.id).id):
            raise Error('abilities.on_cooldown', u'Вы пока не можете использовать эту способность')

    @property
    def ability(self):
        if self.ability_type in ABILITIES:
            return ABILITIES[self.ability_type].get_by_hero_id(HeroPrototype.get_by_account_id(self.account.id).id)
        return None

    @handler('#ability_type', 'form', method='get')
    def form(self):

        form = self.ability.create_form(self)

        return self.template(self.ability.TEMPLATE,
                             {'form': form,
                              'ability': self.ability} )

    @handler('#ability_type', 'activate', method='post')
    def activate(self):

        form = self.ability.create_form(self)

        if form.is_valid():

            if form.c.hero_id != HeroPrototype.get_by_account_id(self.account.id).id:
                return self.json_error('abilities.activate.not_owner', u'Вы пытаетесь провести операцию для чужого героя, ай-яй-яй, как нехорошо!')

            task = self.ability.activate(form, self.time)

            return self.json_processing(task.status_url)

        return self.json_error('abilities.form_errors', form.errors)
