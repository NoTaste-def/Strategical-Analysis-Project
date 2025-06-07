import datetime
import math
import random

from pyjevsim import BehaviorModel, Infinite
from utils.object_db import ObjectDB

from .stationary_decoy import StationaryDecoy
from .self_propelled_decoy import SelfPropelledDecoy
from ..mobject.stationary_decoy_object import StationaryDecoyObject
from ..mobject.self_propelled_decoy_object import SelfPropelledDecoyObject

class Launcher(BehaviorModel):
    def __init__(self, name, platform):
        BehaviorModel.__init__(self, name)
        
        self.platform = platform
        
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Launch", 0)

        self.insert_input_port("order")

        self.launch_flag = False
        self.launch_patterns = {
            "stationary": [
                {"elevation": 45, "azimuth": 0, "speed": 7, "lifespan": 10},
                {"elevation": 45, "azimuth": 180, "speed": 7, "lifespan": 10}
            ],
            "self_propelled": [
                {"elevation": 45, "azimuth": 45, "speed": 10, "lifespan": 10, "heading": 270, "xy_speed": 2},
                {"elevation": 45, "azimuth": 180, "speed": 10, "lifespan": 10, "heading": 180, "xy_speed": 2},
                {"elevation": 45, "azimuth": 315, "speed": 10, "lifespan": 10, "heading": 315, "xy_speed": 2}
            ]
        }
        self.pattern_index = 0

    def get_launch_pattern(self, decoy_type):
        patterns = self.launch_patterns[decoy_type]
        pattern = patterns[self.pattern_index % len(patterns)]
        self.pattern_index += 1
        return pattern

    def ext_trans(self,port, msg):
        if port == "order":
            print(f"{self.get_name()}[order_recv]: {datetime.datetime.now()}")
            self._cur_state = "Launch"
            self.launch_flag = False

    def output(self, msg):
        if not self.launch_flag:
            se = ObjectDB().get_executor()

            for idx, decoy in enumerate(self.platform.lo.get_decoy_list()):
                destroy_t = math.ceil(decoy['lifespan'])
                
                # 발사 패턴 선택
                launch_pattern = self.get_launch_pattern(decoy["type"])
                decoy.update(launch_pattern)
                
                if decoy["type"] == "stationary":
                    sdo = StationaryDecoyObject(self.platform.get_position(), decoy)
                    decoy_model = StationaryDecoy(f"[Decoy][{idx}]", sdo)
                elif decoy["type"] == "self_propelled":
                    sdo = SelfPropelledDecoyObject(self.platform.get_position(), decoy)
                    decoy_model = SelfPropelledDecoy(f"[Decoy][{idx}]", sdo)
                else:
                    sdo = None
                
                if sdo:
                    ObjectDB().decoys.append((f"[Decoy][{idx}]", sdo))
                    ObjectDB().items.append(sdo)
                    se.register_entity(decoy_model, 0, destroy_t)
                
        self.launch_flag = True
        return None
        
    def int_trans(self):
        if self._cur_state == "Launch":
            self._cur_state = "Wait"