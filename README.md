# CBC PADDING CRACKER

This python script exploits the padding vulnerability of AES CBC encryption. It was designed to solve a CTF challenge.
To read details about AES Oracle Padding Attack, click [here](https://en.wikipedia.org/wiki/Padding_oracle_attack).

## Usage
Here is an example for a GET api oracle, where the oracle is called at `http://example.com/index.php?c=<input-data>`:
```bash
python cbc-cracker.py -u "http://example.com/index.php" -m GET -d "c=" -b 16 -c 59873749DC0D3A4ACC7F19D711853685EFCDBFECDF85D6B3AF6171F793CC20B4 -e "Padding Error" -v
```

And here is on for a tcp socket connection oracle at address `example.com` and port `1234`:
```bash
python cbc-cracker.py -u "example.com:1234" -m SOCKET -b 16 -c BC16542433100D9522DC3B6428D4FF5F7FC67B4994323C47ED09F185C3CE7A2E -e "Padding Error" -v
```

TODO:
- verfify if encryption works for more than one block (I'm not sure) 
- handle POST method