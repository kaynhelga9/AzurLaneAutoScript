from module.base.base import ModuleBase
from module.base.switch import Switch
from module.base.utils import color_bar_percentage
from module.handler.assets import *
from module.logger import logger
from module.map.exception import ScriptEnd

fast_forward = Switch('Fast_Forward')
fast_forward.add_status('on', check_button=FAST_FORWARD_ON)
fast_forward.add_status('off', check_button=FAST_FORWARD_OFF)
fleet_lock = Switch('Fleet_Lock')
fleet_lock.add_status('on', check_button=FLEET_LOCKED)
fleet_lock.add_status('off', check_button=FLEET_UNLOCKED)


class FastForwardHandler(ModuleBase):
    def handle_fast_forward(self):
        if not self.appear(MAP_STAR_1) or not self.appear(MAP_STAR_2) or not self.appear(MAP_STAR_3):
            logger.info('Campaign is not 3-star cleared.')
            return False
        if not self.appear(MAP_GREEN):
            logger.info('Campaign is not green sea.')
            return False

        if not fast_forward.appear(main=self):
            self.config.ENABLE_FAST_FORWARD = False
            self.config.MAP_HAS_AMBUSH = True
            logger.info('No fast forward mode.')
            return False

        logger.info('Set fast forward.')
        self.config.MAP_HAS_FLEET_STEP = False
        if self.config.ENABLE_FAST_FORWARD:
            self.config.MAP_HAS_AMBUSH = False
            status = 'on'
        else:
            # When disable fast forward, MAP_HAS_AMBUSH depends on map settings.
            # self.config.MAP_HAS_AMBUSH = True
            status = 'off'
        changed = fast_forward.set(status=status, main=self)
        return changed

    def handle_map_fleet_lock(self):
        if not fleet_lock.appear(main=self):
            logger.info('No fleet lock option.')
            return False

        logger.info('fleet_lock')
        self.config.MAP_HAS_AMBUSH = False
        status = 'on' if self.config.ENABLE_MAP_FLEET_LOCK else 'off'
        changed = fleet_lock.set(status=status, main=self)
        return changed

    def handle_map_clear_mode_stop(self):
        if not self.config.ENABLE_MAP_CLEAR_MODE:
            return False

        percent = color_bar_percentage(self.device.image, area=MAP_CLEAR_PERCENTAGE.area, prev_color=(231, 170, 82))
        logger.attr('Map_clear', f'{int(percent * 100)}%')
        if self.config.CLEAR_MODE_STOP_CONDITION == 'map_100':
            if percent > 0.95:
                raise ScriptEnd(f'Reach condition: {self.config.CLEAR_MODE_STOP_CONDITION}')

        if self.config.CLEAR_MODE_STOP_CONDITION == 'map_3_star':
            if self.appear(MAP_STAR_1) and self.appear(MAP_STAR_2) and self.appear(MAP_STAR_3):
                raise ScriptEnd(f'Reach condition: {self.config.CLEAR_MODE_STOP_CONDITION}')

        if self.config.CLEAR_MODE_STOP_CONDITION in ['map_3_star', 'map_green'] and self.config.MAP_STAR_CLEAR_ALL:
            button = [MAP_STAR_1, MAP_STAR_2, MAP_STAR_3][self.config.MAP_STAR_CLEAR_ALL - 1]
            self.config.MAP_CLEAR_ALL_THIS_TIME = not self.appear(button)
            logger.attr('MAP_CLEAR_ALL_THIS_TIME', self.config.MAP_CLEAR_ALL_THIS_TIME)

        if self.config.CLEAR_MODE_STOP_CONDITION == 'map_green':
            if self.appear(MAP_GREEN):
                raise ScriptEnd(f'Reach condition: {self.config.CLEAR_MODE_STOP_CONDITION}')