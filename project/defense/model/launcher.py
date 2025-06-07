from pyjevsim import BehaviorModel, Infinite
from utils.object_db import ObjectDB
from .stationary_decoy import StationaryDecoy
from .self_propelled_decoy import SelfPropelledDecoy
from ..mobject.stationary_decoy_object import StationaryDecoyObject
from ..mobject.self_propelled_decoy_object import SelfPropelledDecoyObject
import datetime, math

class Launcher(BehaviorModel):
    def __init__(self, name, platform):
        super().__init__(name)
        self.platform = platform
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Launch", 0)
        self.insert_input_port("order")
        self.launch_count = 0  # ✅ 중복 발사 방지용

    def ext_trans(self, port, msg):
        if port == "order" and self.launch_count == 0:
            print(f"{self.get_name()}[order_recv]: {datetime.datetime.now()}")
            self._cur_state = "Launch"

    def output(self, msg):
        se = ObjectDB().get_executor()
        decoy_list = self.platform.lo.get_decoy_list()

        # ✅ 수상함 heading/speed 위장 적용
        ship_heading = self.platform.mo.heading
        ship_speed = self.platform.mo.xy_speed

        for idx, decoy in enumerate(decoy_list):
            decoy["heading"] = ship_heading
            decoy["xy_speed"] = ship_speed

            if decoy["type"] == "stationary":
                sdo = StationaryDecoyObject(self.platform.get_position(), decoy)
                model = StationaryDecoy(f"[Decoy][{idx}]", sdo)

            elif decoy["type"] == "self_propelled":
                sdo = SelfPropelledDecoyObject(self.platform.get_position(), decoy)
                sdo.__class__.__name__ = "SurfaceShipObject"  # ✅ 핵심 위장
                model = SelfPropelledDecoy(f"[Decoy][{idx}]", sdo)

            else:
                continue

            destroy_t = math.ceil(decoy["lifespan"])
            ObjectDB().decoys.append((f"[Decoy][{idx}]", sdo))
            ObjectDB().items.append(sdo)
            se.register_entity(model, 0, destroy_t)
            print(f"[Launcher] Launched: {idx}")

        # ✅ 발사 완료 후 중복 방지 플래그 설정
        self.launch_count += 1
        return None

    def int_trans(self):
        if self._cur_state == "Launch":
            self._cur_state = "Wait"