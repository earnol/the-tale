# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks import PostponedTaskPrototype, autodiscover

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE

from the_tale.game.logic import create_test_map

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.accounts.clans.conf import clans_settings

from the_tale.accounts.payments.postponed_tasks import BuyPremium, BuyPermanentPurchase, BuyRechooseHeroAbilitiesChoices
from the_tale.accounts.payments.goods import PremiumDays, PermanentPurchase, RechooseHeroAbilitiesChoices
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.relations import PERMANENT_PURCHASE_TYPE
from the_tale.accounts.payments.conf import payments_settings

from the_tale.game.heroes.prototypes import HeroPrototype


class PremiumDaysTests(testcase.TestCase):

    def setUp(self):
        super(PremiumDaysTests, self).setUp()

        autodiscover()

        create_test_map()

        self.days = 30
        self.cost = 130

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.hero = HeroPrototype.get_by_account_id(account_id)

        self.purchase = PremiumDays(uid='premium-days-uid',
                                    name=u'premium-days-name',
                                    description=u'premium-days-description',
                                    cost=int(self.cost / payments_settings.GLOBAL_COST_MULTIPLIER),
                                    days=self.days,
                                    transaction_description='premium-days-transaction-description')

    def test_create(self):
        self.assertEqual(self.purchase.uid, 'premium-days-uid')
        self.assertEqual(self.purchase.days, self.days)
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, u'premium-days-name')
        self.assertEqual(self.purchase.description, u'premium-days-description')
        self.assertEqual(self.purchase.transaction_description, u'premium-days-transaction-description')

    def test_buy__fast_account(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        self.account.is_fast = True
        self.account.save()

        self.assertRaises(exceptions.FastAccountError, self.purchase.buy, account=self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)


    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('the_tale.common.postponed_tasks.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account=self.account)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._db_get_object(0).internal_logic

        self.assertTrue(isinstance(postponed_logic, BuyPremium))
        self.assertEqual(postponed_logic.account_id, self.account.id)
        self.assertEqual(postponed_logic.days, self.days)

        invoice = InvoicePrototype.get_by_id(postponed_logic.transaction.invoice_id)

        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 0)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, -self.cost)
        self.assertEqual(invoice.description, u'premium-days-transaction-description')

    def test_is_purchasable(self):
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))



# THIS TESTS NOW IS SPECIFIC TO CLAN_OWNERSHIP_RIGHT
# TODO: rewrite to more abstract tests
class PermanentPurchaseTests(testcase.TestCase):

    PURCHASE_TYPE = PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT

    def setUp(self):
        super(PermanentPurchaseTests, self).setUp()

        autodiscover()

        create_test_map()

        self.cost = 130

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.hero = HeroPrototype.get_by_account_id(account_id)

        self.purchase = PermanentPurchase(uid=u'clan-creation-rights',
                                          name=self.PURCHASE_TYPE.text,
                                          description=self.PURCHASE_TYPE.description,
                                          cost=int(self.cost / payments_settings.GLOBAL_COST_MULTIPLIER),
                                          purchase_type=self.PURCHASE_TYPE,
                                          transaction_description=u'clan-creation-rights')


    def test_create(self):
        self.assertEqual(self.purchase.uid, u'clan-creation-rights')
        self.assertEqual(self.purchase.purchase_type, self.PURCHASE_TYPE)
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, self.PURCHASE_TYPE.text)
        self.assertEqual(self.purchase.description, self.PURCHASE_TYPE.description)
        self.assertEqual(self.purchase.transaction_description, u'clan-creation-rights')

    def test_buy__fast_account(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        self.account.is_fast = True
        self.account.save()

        self.assertRaises(exceptions.FastAccountError, self.purchase.buy, account=self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)


    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('the_tale.common.postponed_tasks.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account=self.account)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._db_get_object(0).internal_logic

        self.assertTrue(isinstance(postponed_logic, BuyPermanentPurchase))
        self.assertEqual(postponed_logic.account_id, self.account.id)
        self.assertEqual(postponed_logic.purchase_type, self.PURCHASE_TYPE)

        invoice = InvoicePrototype.get_by_id(postponed_logic.transaction.invoice_id)

        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 0)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, -self.cost)
        self.assertEqual(invoice.description, u'clan-creation-rights')

    def test_is_purchasable(self):
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))

    def test_is_purchasable__already_purchased(self):
        self.account.permanent_purchases.insert(self.PURCHASE_TYPE)
        self.assertFalse(self.purchase.is_purchasable(self.account, self.hero))

    # TODO: other purchases must be checked in same way
    def test_is_purchasable__have_might(self):
        self.account.set_might(clans_settings.OWNER_MIGHT_REQUIRED)
        self.assertFalse(self.purchase.is_purchasable(self.account, self.hero))


class RechooseHeroAbilitiesChoicesTests(testcase.TestCase):

    def setUp(self):
        super(RechooseHeroAbilitiesChoicesTests, self).setUp()

        autodiscover()

        create_test_map()

        self.cost = 50

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.hero = HeroPrototype.get_by_account_id(account_id)

        self.purchase = RechooseHeroAbilitiesChoices(uid='rechoose-uid',
                                                     name=u'rechoose-name',
                                                     description=u'rechoose-description',
                                                     cost=int(self.cost / payments_settings.GLOBAL_COST_MULTIPLIER),
                                                     transaction_description='rechoose-transaction-description')

    def test_create(self):
        self.assertEqual(self.purchase.uid, 'rechoose-uid')
        self.assertEqual(self.purchase.cost, self.cost)
        self.assertEqual(self.purchase.name, u'rechoose-name')
        self.assertEqual(self.purchase.description, u'rechoose-description')
        self.assertEqual(self.purchase.transaction_description, u'rechoose-transaction-description')

    def test_buy__fast_account(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        self.account.is_fast = True
        self.account.save()

        self.assertRaises(exceptions.FastAccountError, self.purchase.buy, account=self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)


    def test_buy(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 0)

        with mock.patch('the_tale.common.postponed_tasks.PostponedTaskPrototype.cmd_wait') as cmd_wait:
            self.purchase.buy(account=self.account)

        self.assertEqual(cmd_wait.call_count, 1)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(InvoicePrototype._model_class.objects.all().count(), 1)

        postponed_logic = PostponedTaskPrototype._db_get_object(0).internal_logic

        self.assertTrue(isinstance(postponed_logic, BuyRechooseHeroAbilitiesChoices))
        self.assertEqual(postponed_logic.account_id, self.account.id)

        invoice = InvoicePrototype.get_by_id(postponed_logic.transaction.invoice_id)

        self.assertEqual(invoice.recipient_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(invoice.recipient_id, self.account.id)
        self.assertEqual(invoice.sender_type, ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(invoice.sender_id, 0)
        self.assertEqual(invoice.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(invoice.amount, -self.cost)
        self.assertEqual(invoice.description, u'rechoose-transaction-description')

    def test_is_purchasable(self):
        self.assertTrue(self.purchase.is_purchasable(self.account, self.hero))

    def test_not_purchasable(self):
        while self.hero.abilities.can_rechoose_abilities_choices():
            self.hero.randomized_level_up(increment_level=True)

        self.assertFalse(self.purchase.is_purchasable(self.account, self.hero))
