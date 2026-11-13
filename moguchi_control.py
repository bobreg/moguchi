import time
import os
from structs import MoguchiData
import copy
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from log import Moguchi_log

SERIAL_PORT = '/dev/ttyUSB0'
SLAVE_ID = 0x01
TARGET_TEMP = 23.0       # Целевая температура в комнате
HYSTERESIS_LOW = 1.0         # Гистерезис
HYSTERESIS_UP = 1.0
SETPOINT_FLOW = 60.0     # Температура воды (уставка для котла)
TEMPERATURE_FILE_PATH = '/sys/bus/w1/devices/28-00000021a8d4/w1_slave'

ENABLE_WARM_HEATERS = 1 << 0
ENABLE_WARM_WATER   = 1 << 1

BURNER_STATE          = 1 << 0
HEATING_CIRCUIT_STATE = 1 << 1
WATER_CIRCUIT_STATE   = 1 << 2
BOILER_STATE          = 1 << 3


class Moguchi:
    def __init__(self):
        self.m_temperature = None
        self.m_work = True
        self.m_temperature_file_path = TEMPERATURE_FILE_PATH
        self.controller = ModbusSerialClient(port=SERIAL_PORT, baudrate=19200, parity='N', stopbits=1, bytesize=8, timeout=1)

        self.m_controller_connect_flag = False
        self.m_boiler_acceped_command_flag = False
        self.m_warm_house_flag = False
        self.m_boiler_change_state_flag = False
        
        self.m_moguchi_data = None
        self.m_log = Moguchi_log()
        self.m_log.msg_info('Moguchi activated!')
        self.connect_to_controller()
        

    def connect_to_controller(self):
        if self.m_controller_connect_flag == False:
            if self.controller.connect():
                self.m_log.msg_info('The controller is alive')
                self.m_controller_connect_flag = True
            else:
                self.m_log.msg_error('There is no controller')

    def read_temperature(self):
        temperature = None
        if os.path.exists(self.m_temperature_file_path):
            try:
                with open(self.m_temperature_file_path, 'r') as file:
                    r = file.read()
                    temperature = int(r.split('t=')[1]) / 1000
            except Exception as e:
                self.m_log.msg_warn(f'Can\'t read temperature sensor - {e}')
        return temperature


    def read_registers(self, addr: int, r_count: int, dev_id: int):
        try:
            rs485_data = self.controller.read_holding_registers(address=addr, count=r_count, device_id=dev_id)
            if not rs485_data.isError():
                return rs485_data
            else:
                self.m_log.msg_warn(f'Registers reading false!')
        except Exception as e:
            self.m_log.msg_error(f'Connection lost! - {e}')

        return None


    def write_register(self, val: int, addr: int, dev_id: int):
        wr = self.controller.write_registers(address=addr, values=[val], device_id=dev_id)
        if wr.isError():
            self.m_log.msg_warn(f'Can\'t write register {addr}, data {val}!')
            return False
        return True


    def read_boiler_data(self):
        m_data = None
        try:
            rs485_data = self.controller.read_holding_registers(address=0x0010, count=16, device_id=SLAVE_ID)
            if not rs485_data.isError():
                boiler_regs = rs485_data.registers
                if (boiler_regs[0] >> 8) & BOILER_STATE:  # the boiler is alive
                    m_data = MoguchiData()
                    m_data.flow_temperature = boiler_regs[8] / 10.0
                    m_data.burner_modulation = boiler_regs[12]
                    m_data.burner_state = (boiler_regs[13] & HEATING_CIRCUIT_STATE) != 0
                    m_data.heating_circuit_state = (boiler_regs[13] & HEATING_CIRCUIT_STATE) != 0
                    m_data.water_circuit_state = (boiler_regs[13] & WATER_CIRCUIT_STATE) != 0

                if self.m_boiler_change_state_flag == True:
                    self.m_log.msg_info('Boiler is alive!')
                    self.m_boiler_change_state_flag = False

        except Exception as e:
            if self.m_boiler_change_state_flag == False:
                self.m_log.msg_info(f'Lost the boiler - {e}')
                self.m_boiler_change_state_flag = True

        return copy.copy(m_data)


    def enable_heat(self, on_flag: bool):
        try:
            rs485_data = self.controller.read_holding_registers(address=0x0039, count=1, device_id=SLAVE_ID)  # read boiler's circuits register
            boiler_circuits_state = rs485_data.registers[0]
            if on_flag:
                boiler_circuits_state |= ENABLE_WARM_HEATERS
            else:
                boiler_circuits_state &= ~(ENABLE_WARM_HEATERS)

            wr = self.controller.write_registers(address=0x0039, values=[boiler_circuits_state], device_id=SLAVE_ID)  # enable heating circuits
            if wr.isError():
                self.m_log.msg_warn("Can't write 0x39 register and enable heat!")
                return False

            time.sleep(1)

            wr = self.controller.write_registers(address=0x0031, values=[int(SETPOINT_FLOW * 10)], device_id=SLAVE_ID)  # enable burner
            if wr.isError():
                self.m_log.msg_warn("Can't write 0x31 register and enable burner!")
                return False
            return True
        
        except Exception as e:
            self.m_log.msg_error(f"Can't read boiler's circuits register - {e}")
            return False


    def warm_house(self):
        if self.m_moguchi_data != None and self.m_temperature != None:  # globally check connection  

            if not self.m_moguchi_data.water_circuit_state:             # check using water          
                if self.m_temperature < TARGET_TEMP - HYSTERESIS_LOW and \
                    not self.m_warm_house_flag:  # enable heat
                    self.m_log.msg_info('Enable house warm')
                    self.m_boiler_acceped_command_flag = self.enable_heat(True)
                    if self.m_boiler_acceped_command_flag:
                        self.m_warm_house_flag = True
                elif self.m_temperature > TARGET_TEMP + HYSTERESIS_UP and \
                    self.m_warm_house_flag:  # disable heat
                    self.m_log.msg_info('Disable house warm')
                    self.m_boiler_acceped_command_flag = self.enable_heat(False)
                    if self.m_boiler_acceped_command_flag:
                        self.m_warm_house_flag = False
            else:
                self.m_warm_house_flag = False


    def work(self):
        if self.m_controller_connect_flag == True:
            while self.m_work == True:
                try:
                    self.m_temperature = self.read_temperature()
                    self.m_moguchi_data = self.read_boiler_data()
                    self.warm_house()
                except Exception as e:
                    self.m_log.msg_error(f"There is a problem Cap - {e}")
                time.sleep(1)

        self.enable_heat(False)
        self.m_log.msg_info("Work thread stop!")


    def get_data(self):
        contex = {
            'temperature': self.m_temperature,
            'flow_temperature': self.m_moguchi_data.flow_temperature if self.m_moguchi_data != None else None,
            'burner_modulation': self.m_moguchi_data.burner_modulation if self.m_moguchi_data != None else None,
            'burner_state': self.m_moguchi_data.burner_state if self.m_moguchi_data != None else None,
            'controller_connection': self.m_controller_connect_flag,
            'boiler_connection': True if self.m_moguchi_data != None else False,
            'temp_sensor': True if self.m_temperature != None else False,
            'warm_house': self.m_warm_house_flag,
            'heating_circuit_state': self.m_moguchi_data.heating_circuit_state if self.m_moguchi_data != None else None,
            'water_circuit_state': self.m_moguchi_data.water_circuit_state if self.m_moguchi_data != None else None
                }
        return contex

def main():
    print("You have to run the Django server from manage.py.")

if __name__ == "__main__":
    main()