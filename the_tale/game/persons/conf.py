# coding: utf-8

from dext.common.utils.app_settings import app_settings

from the_tale.game.balance import constants as c

POWER_HISTORY_WEEKS = 8

settings = app_settings('PERSONS',
                        POWER_HISTORY_WEEKS=POWER_HISTORY_WEEKS,
                        POWER_HISTORY_LENGTH=int(POWER_HISTORY_WEEKS*7*24*c.TURNS_IN_HOUR),
                        POWER_STABILITY_PERCENT=0.05,
                        POWER_STABILITY_WEEKS=2,
                        SOCIAL_CONNECTIONS_MINIMUM=3,
                        SOCIAL_CONNECTIONS_AVERAGE_PATH_FRACTION=0.75,
                        SOCIAL_CONNECTIONS_MIN_DISTANCE_DECREASE=0.9)
