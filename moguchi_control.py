import time
import os
from structs import MoguchiData
import copy
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

SERIAL_PORT = '/dev/ttyUSB0'
SLAVE_ID = 0x01
TARGET_TEMP = 23.0       # Целевая температура в комнате
HYSTERESIS_LOW = 1.0         # Гистерезис
HYSTERESIS_UP = 1.0
SETPOINT_FLOW = 60.0     # Температура воды (уставка для котла)
TEMPERATURE_FILE_PATH = '/sys/bus/w1/devices/28-00000021a8d4/w1_slave'

ENABLE_WARM_HEATERS = 1 << 0
ENABLE_WARM_WATER   = 1 << 1

BURNER_STATE = 1 << 0
HEATING_CIRCUIT_STATE = 1 << 0
WATER_CIRCUIT_STATE = 1 << 0

'''
def set_heating(client, enabled: bool):
    try:
        rr = client.read_holding_registers(address=0x0039, count=1, device_id=SLAVE_ID)
        if rr.isError(): return False

        current = rr.registers[0]
        new_val = (current | 0x0001) if enabled else (current & 0xFFFE)

        if new_val != current:
            # ВАЖНО: используем write_registers и передаем список [new_val]
            wr = client.write_registers(address=0x0039, values=[new_val], device_id=SLAVE_ID)
            if wr.isError():
                print(f"❌ Ошибка записи 0x0039: {wr}")
                return False
            print(f"✅ Запись 0x0039 успешна: {new_val}")
        return True
    except ModbusIOException:
        print("⚠️ Таймаут при записи 0x0039")
        return False

def set_flow_temp(client, temp_c):
    try:
        # Исправлено: write_registers и передача в списке
        wr = client.write_registers(address=0x0031, values=[int(temp_c * 10)], device_id=SLAVE_ID)
        if wr.isError():
            print(f"❌ Ошибка записи уставки 0x0031: {wr}")
    except ModbusIOException:
        print("⚠️ Таймаут при записи 0x0031")

# --- Основной цикл ---
client = ModbusSerialClient(port=SERIAL_PORT, baudrate=19200, parity='N', stopbits=1, bytesize=8, timeout=1)

if not client.connect():
    print("❌ Нет связи с USB-RS485")
    exit(1)

print(f"✅ Связь есть. Целевая температура: {TARGET_TEMP}°C. Ждём данные...")
heating_on = None

try:
    while True:
        room_temp = read_ds18b20()

        try:
            # Читаем данные
            rr = client.read_holding_registers(address=0x0010, count=16, device_id=SLAVE_ID)

            if not rr.isError():
                reg = rr.registers

                # В дампе 0x0010 было 0x0800 (2048). Убираем проверку бита,
                # так как данные реально идут (мы видим температуру подачи).
                # Считаем, что связь есть, если чтение не вернуло ошибку.

                flow_temp = reg[8] / 10.0
                modulation = reg[12]
                burner = reg[13] & 0x01

                if room_temp is not None:
                    print(f"🏠 В комнате: {room_temp:.1f}°C | 🔥 Подача: {flow_temp:.1f}°C | Горелка: {'ВКЛ' if burner else 'ВЫКЛ'} | Мод: {modulation}%")

                    if room_temp < TARGET_TEMP - HYSTERESIS_LOW and heating_on != True:
                        print("🥶 Холодно! Включаем отопление.")
                        if set_heating(client, True):
                            time.sleep(0.5) # Пауза между командами
                            set_flow_temp(client, SETPOINT_FLOW)
                            heating_on = True

                    elif room_temp > TARGET_TEMP + HYSTERESIS_UP and heating_on != False:
                        print("🥵 Тепло! Выключаем отопление.")
                        if set_heating(client, False):
                            heating_on = False

        except ModbusIOException:
            print("⚠️ Пропуск цикла: таймаут связи с адаптером")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nОстановлено. Выключаем отопление...")
    set_heating(client, False)
    print("Готово.")
finally:
    client.close()
'''


class Moguchi:
    def __init__(self):
        self.m_temperature = None
        self.m_work = True
        self.m_temperature_file_path = TEMPERATURE_FILE_PATH
        self.controller = ModbusSerialClient(port=SERIAL_PORT, baudrate=19200, parity='N', stopbits=1, bytesize=8, timeout=1)

        self.m_controller_connect_flag = False
        self.m_boiler_acceped_command_flag = False
        self.m_warm_house_flag = False
        
        self.m_moguchi_data = None

        self.connect_to_controller()
        

    def connect_to_controller(self):
        if self.m_controller_connect_flag == False:
            if self.controller.connect():
                print('The controller is alive')
                self.m_controller_connect_flag = True
            else:
                print('There is no controller')

    def read_temperature(self):
        temperature = None
        if os.path.exists(self.m_temperature_file_path):
            with open(self.m_temperature_file_path, 'r') as file:
                r = file.read()
                temperature = int(r.split('t=')[1]) / 1000
        return temperature


    def read_boiler_data(self):
        m_data = None
        try:
            rs485_data = self.controller.read_holding_registers(address=0x0010, count=16, device_id=SLAVE_ID)

            if not rs485_data.isError():
                boiler_regs = rs485_data.registers
                if (boiler_regs[0] >> 8) | 0x1000:  # the boiler is alive
                    m_data = MoguchiData()
                    m_data.flow_temperature = boiler_regs[8] / 10.0
                    m_data.burner_modulation = boiler_regs[12]
                    m_data.burner_state = (boiler_regs[13] & 0x1 == 1)
                    m_data.heating_circuit_state = True if boiler_regs[13] & 0x10 else False
                    m_data.water_circuit_state = True if boiler_regs[13] & 0x100 else False
                else:
                    print(hex(boiler_regs[0]))
        except:
            pass

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
                print("Can't write 0x39 register and enable heat!")
                return False

            time.sleep(1)

            wr = self.controller.write_registers(address=0x0031, values=[int(SETPOINT_FLOW * 10)], device_id=SLAVE_ID)  # enable burner
            if wr.isError():
                print("Can't write 0x31 register and enable burner!")
                return False
            return True
        
        except:
            print("Can't read boiler's circuits register")
            return False


    def warm_house(self):
        if self.m_moguchi_data != None and self.m_temperature != None:  # globally check connection  

            if not self.m_moguchi_data.water_circuit_state:             # check using water          
                if self.m_temperature < TARGET_TEMP - HYSTERESIS_LOW and \
                    not self.m_warm_house_flag:  # enable heat
                    print('Enable house warm')
                    self.m_boiler_acceped_command_flag = self.enable_heat(True)
                    if self.m_boiler_acceped_command_flag:
                        self.m_warm_house_flag = True
                elif self.m_temperature > TARGET_TEMP + HYSTERESIS_UP and \
                    self.m_warm_house_flag:  # disable heat
                    print('Disable house warm')
                    self.m_boiler_acceped_command_flag = self.enable_heat(False)
                    if self.m_boiler_acceped_command_flag:
                        self.m_warm_house_flag = False
            else:
                self.m_warm_house_flag = False


    def work(self):
        if self.m_controller_connect_flag == True:
            while self.m_work == True:
                self.m_temperature = self.read_temperature()
                self.m_moguchi_data = self.read_boiler_data()

                self.warm_house()

                time.sleep(1)

        self.enable_heat(False)
        print("Work thread stop!")


    def get_data(self):
        contex = {
            'temperature': self.m_temperature,
            'flow_temperature': self.m_moguchi_data.flow_temperature if self.m_moguchi_data != None else None,
            'burner_modulation': self.m_moguchi_data.burner_modulation if self.m_moguchi_data != None else None,
            'burner_state': self.m_moguchi_data.burner_state if self.m_moguchi_data != None else None,
            'controller_connection': self.m_controller_connect_flag,
            'boiler_connection': True if self.m_moguchi_data != None else False,
            'boiler_accepted_command': self.m_boiler_acceped_command_flag,
            'temp_sensor': True if self.m_temperature != None else False,
            'warm_house': self.m_warm_house_flag,
            'target_flow_temperature': SETPOINT_FLOW,
            'heating_circuit_state': self.m_moguchi_data.heating_circuit_state if self.m_moguchi_data != None else None,
            'water_circuit_state': self.m_moguchi_data.water_circuit_state if self.m_moguchi_data != None else None
                }
        return contex

def main():
    print("You have to run the Django server from manage.py.")

if __name__ == "__main__":
    main()