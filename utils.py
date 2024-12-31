import argparse
import hashlib
import json


ORANGE = "\033[38;5;214m"
WHITE = "\033[37m"
GREEN = "\033[32m"
RED = "\033[31m"


ban = """

---------------------------------------------------------------------------------

 ██████╗██████╗  ██████╗    ██████╗  █████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗     
██╔════╝██╔══██╗██╔════╝    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝     
██║     ██████╔╝██║         ██████╔╝███████║██║  ██║██║  ██║██║██╔██╗ ██║██║  ███╗    
██║     ██╔══██╗██║         ██╔═══╝ ██╔══██║██║  ██║██║  ██║██║██║╚██╗██║██║   ██║    
╚██████╗██████╔╝╚██████╗    ██║     ██║  ██║██████╔╝██████╔╝██║██║ ╚████║╚██████╔╝    
 ╚═════╝╚═════╝  ╚═════╝    ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝     
                                                                                      
             ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗                               
            ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗                              
            ██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝                              
            ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗                              
            ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║                              
             ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                              


----------------------------------By b3liott-------------------------------------                                                                                              

"""


def hex_to_binary(hex_str):
    decimal_value = int(hex_str, 16)
    binary_str = bin(decimal_value)[2:]
    return binary_str

def blockToCypher(blocks):
    c = ""
    for b in blocks:
        c += b
    return c


def log_error(message):
    print(f"{RED}Error: {message}{WHITE}")

def log_success(message):
    print(f"{GREEN}{message}{WHITE}")

def getFileName(url, cypher):
    return hashlib.md5((url+cypher).encode("utf-8")).hexdigest()

def save_data(saved_data, url, cypher):
    try:
        with open(f"save/{getFileName(url, cypher)}", 'w') as f:
            json.dump(saved_data, f, indent=4)
    except Exception as e:
        log_error(f"Erreur lors de la sauvegarde: {e}")

def read_data(file_name):
    try:
        with open(f"save/{file_name}", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        log_error(f"Erreur lors de la lecture: {e}")
        return None

def get_args() -> list:
    parser = argparse.ArgumentParser(description='Oracle padding attack tool')
    parser.add_argument('-u', '--url', type=str, help='Url pointing to the oracle', required=True)
    parser.add_argument('-m', '--method', type=str, choices=['GET', 'POST', 'SOCKET'], help='SOCKET, GET or POST method to interact with the oracle', required=True)
    parser.add_argument('-d', '--data', type=str, help='Data to be sent to interact with the oracle.\nFor data c= with get we have:\nexample.com/index.php?c=\nWith post we have c= in the body\n', required=False)
    parser.add_argument('-c', '--cypher', type=str, help='Cypher text', required=True)
    parser.add_argument('-b', '--block-size', type=int, help='block size (8, 16, 32 ...)', required=True)
    parser.add_argument('-e', '--padding-error', type=str, help='Padding error text, inside the html response', required=True)
    parser.add_argument('-v', '--verbose', action="store_true", help='Display fancy infos')

    args = parser.parse_args()
    if args.method != 'SOCKET' and not args.data:
        parser.error("-d (--data) argument is required for GET or POST method.")

    return args.url, args.method, args.data, args.cypher, args.block_size, args.padding_error, args.verbose