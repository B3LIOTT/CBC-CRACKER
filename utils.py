import argparse


ORANGE = "\033[38;5;214m"
WHITE = "\033[37m"
GREEN = "\033[32m"
RED = "\033[31m"

def log_error(message):
    print(f"{RED}Error: {message}{WHITE}")

def get_args() -> list:
    parser = argparse.ArgumentParser(description='Oracle padding attack tool')
    parser.add_argument('-u', '--url', type=str, help='Url pointing to the oracle', required=True)
    parser.add_argument('-m', '--method', type=str, help='GET or POST method to interact with the oracle', required=True)
    parser.add_argument('-d', '--data', type=str, help='Data to be sent to interact with the oracle.\nFor data c= with get we have:\nexample.com/index.php?c=\nWith post we have c= in the body\n', required=True)
    parser.add_argument('-c', '--cypher', type=str, help='Cypher text', required=True)
    parser.add_argument('-b', '--block-size', type=int, help='block size (8, 16, 32 ...)', required=True)

    args = parser.parse_args()
    return args.url, args.method, args.data, args.cypher, args.block_size 