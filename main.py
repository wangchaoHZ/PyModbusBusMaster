import logging
import random
import time
from os import times

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from datetime import datetime

# Configure logging with dynamic log file name based on current time
def configure_logging():
    log_file = f"mb_master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


mb_master_client = None

def convert_to_unsigned(value):
    if -32768 <= value < 0:  # For negative values
        return 65536 + value
    elif 0 <= value <= 65535:  # For non-negative values
        return value
    else:
        raise ValueError(f"Value {value} out of range for 16-bit Modbus register")


def write_single_register(address, value, slave_id=1):
    try:
        # Convert signed integer to unsigned if necessary
        unsigned_value = convert_to_unsigned(value)

        # Write single register (Function code 06)
        response = mb_master_client.write_register(address, unsigned_value, slave=slave_id)

        # Check if response is valid
        if response.isError():
            msg = f"Write failed: Address={address}, Value={value} (Unsigned={unsigned_value}), Slave ID={slave_id}"
            print(msg)
            logging.error(msg)
            return False
        else:
            msg = f"Write successful: Address={address}, Value={value} (Unsigned={unsigned_value}), Slave ID={slave_id}"
            print(msg)
            logging.info(msg)
            return True

    except ModbusException as e:
        msg = f"Modbus exception: {e}"
        print(msg)
        logging.error(msg)
        return False
    except ValueError as ve:
        msg = f"Value error: {ve}"
        print(msg)
        logging.error(msg)
        return False
    except Exception as ex:
        msg = f"Unexpected error: {ex}"
        print(msg)
        logging.error(msg)
        return False
    finally:
        pass


def generate_random_value():
    return random.randint(-60, 60)


def send_multiple_requests(slave_id, address_values, delays, retries=1):
    for i in range(1, retries + 1):
        logging.info(f"Attempt {i} of {retries}")
        for address, value in address_values:
            if address == 400 or address == 401:
                vt = value + generate_random_value()
                success = write_single_register(address, vt, slave_id)
                if success:
                    logging.info(f"Successfully wrote Address={address}, Value={value}")
                else:
                    logging.error(f"Failed to write Address={address}, Value={value}")
            else:
                success = write_single_register(address, value, slave_id)
                if success:
                    logging.info(f"Successfully wrote Address={address}, Value={value}")
                else:
                    logging.error(f"Failed to write Address={address}, Value={value}")
        time.sleep(delays)
    logging.info(f"All Have Complete {retries}")
    mb_master_client.close()


# Main program
if __name__ == "__main__":
    configure_logging()

    # server_host = "192.168.1.122"  # Modbus server IP

    server_host = "127.0.0.1"  # Modbus server IP
    server_port = 502  # Modbus TCP default port
    slave_id = 17  # Modbus slave ID
    #
    retry = 100  # Number of send attempts

    # Create Modbus TCP client
    mb_master_client = ModbusTcpClient(host=server_host, port=server_port)

    # Attempt to connect to the server
    if not mb_master_client.connect():
        msg = f"Failed to connect to Modbus server {server_host}:{server_port}"
        print(msg)
        logging.error(msg)
    else:
        msg = f"Successfully to connect to Modbus server {server_host}:{server_port}"
        print(msg)
        logging.error(msg)
        # List of registers and values to write (includes negative values)
        address_values = [
            (400, -2323),  # Branch 1
            (401, -2345),  # Branch 2 (negative value)
            (402, 0x00)  # Leak word
        ]
        send_multiple_requests(slave_id, address_values, delays=1, retries=retry)
