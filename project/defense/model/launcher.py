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

    def ext_trans(self, port, msg):
        if port == "order":
            print(f"{self.get_name()}[order_recv]: {datetime.datetime.now()}")
            self._cur_state = "Launch"

    def output(self, msg):
        if not self.launch_flag:
            se = ObjectDB().get_executor()
            decoy_list = self.platform.lo.get_decoy_list()

            # Surface ship 방향 가져오기 (현재 heading 추정치)
            surface_heading = getattr(self.platform, "heading", 0)

            for idx, decoy in enumerate(decoy_list):
                destroy_t = math.ceil(decoy['lifespan'])

                # 하나의 decoy만 surface ship 방향을 따라가게 설정
                if idx == 0 and "heading" in decoy:
                    decoy["heading"] = surface_heading  # surface ship과 동일하게 설정

                if decoy["type"] == "stationary":
                    sdo = StationaryDecoyObject(self.platform.get_position(), decoy)
                    decoy_model = StationaryDecoy(f"[Decoy][{idx}]", sdo)
                elif decoy["type"] == "self_propelled":
                    sdo = SelfPropelledDecoyObject(self.platform.get_position(), decoy)
                    decoy_model = SelfPropelledDecoy(f"[Decoy][{idx}]", sdo)
                else:
                    sdo = None

                ObjectDB().decoys.append((f"[Decoy][{idx}]", sdo))
                ObjectDB().items.append(sdo)
                se.register_entity(decoy_model, 0, destroy_t)

            self.launch_flag = True

        return None


    def int_trans(self):
        if self._cur_state == "Launch":
            self._cur_state = "Wait"
