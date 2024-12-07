import logging
import random

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from datetime import datetime


# Configure logging with dynamic log file name based on current time
def configure_logging():
    log_file = f"modbus_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def convert_to_unsigned(value):
    """
    Converts a signed integer to its 16-bit unsigned representation.

    Args:
        value (int): The signed integer to convert.

    Returns:
        int: The unsigned 16-bit integer representation.
    """
    if -32768 <= value < 0:  # For negative values
        return 65536 + value
    elif 0 <= value <= 65535:  # For non-negative values
        return value
    else:
        raise ValueError(f"Value {value} out of range for 16-bit Modbus register")


def write_single_register(host, port, address, value, slave_id=1):
    """
    Writes a single holding register on the Modbus server.

    Args:
        host (str): Modbus server IP address.
        port (int): Modbus server port (default 502).
        address (int): Register address.
        value (int): Value to write (supports signed integers).
        slave_id (int): Modbus slave ID (default 1).

    Returns:
        bool: True if the write operation is successful, False otherwise.
    """
    client = None
    try:
        # Convert signed integer to unsigned if necessary
        unsigned_value = convert_to_unsigned(value)

        # Create Modbus TCP client
        client = ModbusTcpClient(host=host, port=port)

        # Attempt to connect to the server
        if not client.connect():
            msg = f"Failed to connect to Modbus server {host}:{port}"
            print(msg)
            logging.error(msg)
            return False

        # Write single register (Function code 06)
        response = client.write_register(address, unsigned_value, slave=slave_id)

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
        if client:
            client.close()


def generate_random_value():
    """
    Generate a random integer between -50 and 50.

    Returns:
        int: Random value.
    """
    return random.randint(-60, 60)


def send_multiple_requests(host, port, slave_id, address_values, retries=1):
    """
    Sends multiple Modbus write requests, retrying in case of failure.

    Args:
        host (str): Modbus server IP address.
        port (int): Modbus server port (default 502).
        slave_id (int): Modbus slave ID.
        address_values (list of tuple): List of (address, value) pairs.
        retries (int): Number of retry attempts on failure (default 1).
    """
    for i in range(1, retries + 1):
        logging.info(f"Attempt {i} of {retries}")
        for address, value in address_values:
            if address == 400 or address == 401:
                vt = value + generate_random_value()
                success = write_single_register(host, port, address, vt, slave_id)
                if success:
                    logging.info(f"Successfully wrote Address={address}, Value={value}")
                else:
                    logging.error(f"Failed to write Address={address}, Value={value}")
            else:
                success = write_single_register(host, port, address, value, slave_id)
                if success:
                    logging.info(f"Successfully wrote Address={address}, Value={value}")
                else:
                    logging.error(f"Failed to write Address={address}, Value={value}")


# Main program
if __name__ == "__main__":
    configure_logging()

    server_host = "192.168.1.122"  # Modbus server IP
    server_port = 502  # Modbus TCP default port
    slave_id = 17  # Modbus slave ID

    # List of registers and values to write (includes negative values)
    address_values = [
        (400, -2323),  # Branch 1
        (401, -2345),  # Branch 2 (negative value)
        (402, 0x00)  # Leak word
    ]

    retries = 100  # Number of send attempts

    send_multiple_requests(server_host, server_port, slave_id, address_values, retries)
