import platform
from pyjevsim import BehaviorModel, Infinite
import datetime
import math

from pyjevsim.system_message import SysMessage

class CommandControl(BehaviorModel):
    def __init__(self, name, platform):
        BehaviorModel.__init__(self, name)
        
        self.platform = platform
        
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Decision", 0)

        self.insert_input_port("threat_list")
        self.insert_output_port("launch_order")

        self.threat_list = []
        self.decoy_cost = 0
        self.max_cost = 10
        self.target_cost = 9.5
        self.stationary_cost = 1
        self.self_propelled_cost = 2.5
        self.initial_deployment = False
        self.emergency_deployment = False
        self.last_launch_time = None
        self.launch_cooldown = 2

    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def evaluate_threat(self, threat):
        distance = self.calculate_distance(
            (self.platform.mo.x, self.platform.mo.y),
            (threat.x, threat.y)
        )
        
        if not self.initial_deployment:
            if self.decoy_cost + self.stationary_cost <= self.target_cost:
                return True, "stationary"
        
        if distance < 25:
            if not self.emergency_deployment and self.decoy_cost + self.self_propelled_cost <= self.target_cost:
                return True, "self_propelled"
        elif distance < 40:
            if self.decoy_cost + self.stationary_cost <= self.target_cost:
                return True, "stationary"
        
        return False, None

    def ext_trans(self,port, msg):
        if port == "threat_list":
            print(f"{self.get_name()}[threat_list]: {datetime.datetime.now()}")
            self.threat_list = msg.retrieve()[0]
            self._cur_state = "Decision"

    def output(self, msg):
        current_time = datetime.datetime.now()
        
        for target in self.threat_list:
            is_threat, decoy_type = self.evaluate_threat(target)
            
            if is_threat:
                if (self.last_launch_time is None or 
                    (current_time - self.last_launch_time).total_seconds() >= self.launch_cooldown):
                    
                    if decoy_type == "self_propelled" and self.decoy_cost + self.self_propelled_cost <= self.target_cost:
                        self.decoy_cost += self.self_propelled_cost
                        message = SysMessage(self.get_name(), "launch_order")
                        msg.insert_message(message)
                        self.last_launch_time = current_time
                        self.emergency_deployment = True
                        
                    elif decoy_type == "stationary" and self.decoy_cost + self.stationary_cost <= self.target_cost:
                        self.decoy_cost += self.stationary_cost
                        message = SysMessage(self.get_name(), "launch_order")
                        msg.insert_message(message)
                        self.last_launch_time = current_time
                        self.initial_deployment = True
                
                self.platform.mo.change_heading(self.platform.co.get_evasion_heading())
        
        self.threat_list = []
        return msg
        
    def int_trans(self):
        if self._cur_state == "Decision":
            self._cur_state = "Wait"