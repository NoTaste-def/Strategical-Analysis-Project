import platform
from pyjevsim import BehaviorModel, Infinite
import datetime

from pyjevsim.system_message import SysMessage

class TorpedoCommandControl(BehaviorModel):
    def __init__(self, name, platform):
        BehaviorModel.__init__(self, name)
        
        self.platform = platform
        
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Decision", 0)

        self.insert_input_port("threat_list")
        self.insert_output_port("target")
        self.threat_list = []

        self.prev_target_positions = {}


    def ext_trans(self,port, msg):
        if port == "threat_list":
            print(f"{self.get_name()}[threat_list]: {datetime.datetime.now()}")
            self.threat_list = msg.retrieve()[0]
            self._cur_state = "Decision"

    def output(self, msg):
        target = None
        
        for t in self.threat_list:
            target =  self.platform.co.get_target(self.platform.mo, t)

                
        # house keeping
        self.threat_list = []
        self.platform.co.reset_target()
        
        if target:
            message = SysMessage(self.get_name(), "target")
            message.insert(target)
            msg.insert_message(message)
        
        return msg
    # def output(self, msg):
    #     target = None

    #     for t in self.threat_list:
    #         cur_pos = self.platform.co.get_target(self.platform.mo, t)
    #         if not cur_pos:
    #             continue

    #         prev_pos = self.prev_target_positions.get(t)

    #         if prev_pos:
    #             x_self, y_self, _ = self.platform.mo.get_position()
    #             x_prev, y_prev, _ = prev_pos
    #             x_cur, y_cur, _ = cur_pos

    #             dx_prev = x_prev - x_self
    #             dy_prev = y_prev - y_self
    #             dist_prev = dx_prev**2 + dy_prev**2

    #             dx_cur = x_cur - x_self
    #             dy_cur = y_cur - y_self
    #             dist_cur = dx_cur**2 + dy_cur**2

    #             if dist_cur > dist_prev:
    #                 target = cur_pos
    #                 break

            # # 이전 좌표 업데이트
            # self.prev_target_positions[t] = cur_pos

        # self.threat_list = []
        # self.platform.co.reset_target()

        # if target:
        #     message = SysMessage(self.get_name(), "target")
        #     message.insert(target)
        #     msg.insert_message(message)

        # return msg
    
    def int_trans(self):
        if self._cur_state == "Decision":
            self._cur_state = "Wait"