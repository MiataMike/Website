pi = 3.14159265

class VehicleConfig:
    def __init__(self,
                 max_mph=128,
                 rpm_limit=5500,
                 tire_diameter_in=30.0,
                 rear_end_ratio=2.73,
                 vss_pulses_per_rev=40):
        self.max_mph = max_mph
        self.rpm_limit = rpm_limit
        self.tire_diameter_in = tire_diameter_in
        self.rear_end_ratio = rear_end_ratio
        self.vss_pulses_per_rev = vss_pulses_per_rev
        self.version = 2
        # 4L60E gear ratios
        self.gear_ratios = {
            1: 3.06,
            2: 1.63,
            3: 1.00,
            4: 0.70
        }

        # Solenoid map (A, B) → bits: A=bit1, B=bit0
        self.solenoid_map = {
            1: 0b10,  # A ON, B OFF
            2: 0b11,  # A ON, B ON
            3: 0b00,  # A OFF, B OFF
            4: 0b01   # A OFF, B ON
        }
        
        self.gear_map = {
            0b00: 3,
            0b01: 1,
            0b10: 4,
            0b11: 2
        }

    def max_speed_for_gear(self, gear: int) -> float:
        tire_circ_ft = (self.tire_diameter_in * np.pi) / 12
        gear_ratio = self.gear_ratios[gear]
        speed_mph = (self.rpm_limit * tire_circ_ft) / (gear_ratio * self.rear_end_ratio * 88)
        return speed_mph

    def vss_frequency(self, speed_mph: float) -> float:
        feet_per_second = speed_mph * 5280 / 3600
        tire_circ_ft = (self.tire_diameter_in * np.pi) / 12
        wheel_rpm = (feet_per_second / tire_circ_ft) * 60
        driveshaft_rpm = wheel_rpm * self.rear_end_ratio
        return (driveshaft_rpm * self.vss_pulses_per_rev) / 60

    def gear_to_solenoid_pattern(self, gear: int) -> int:
        return self.solenoid_map.get(gear, 0b00)
    
    def solenoid_pattern_to_gear(self, pattern: int) -> int:
        return self.gear_map.get(pattern)