from bits import constants
from typing import List


def parse_inscriptions(witness_element: bytes | str) -> List[dict]:
    """
    Parse witness stack element for inscriptions
    Args:
        witness_element: bytes | str, The witness stack element to parse
    Returns:
        List[dict]: List of inscriptions
            dict for each inscription, respectively, contains keys:
                content_type: str
                data: bytes
                delegate: bytes
                metadata: bytes
                pointer: bytes
                properties: bytes
    """
    if type(witness_element) is str:
        witness_element = bytes.fromhex(witness_element)
    inscriptions = []
    ord_envelope_begin = witness_element.find(
        b"\x00\x63\x03ord"
    )  # OP_FALSE OP_IF OP_PUSHBYTES3 ord
    while ord_envelope_begin != -1:
        inscription = {}

        witness_element = witness_element[ord_envelope_begin:]
        witness_element = witness_element[
            6:
        ]  # skip 'OP_FALSE OP_IF OP_PUSHBYTES3 ord' preamble

        while witness_element and witness_element[0] != constants.OP_ENDIF:
            # parse the OP_PUSH and tag
            if witness_element[0] in range(1, 0x4C):
                push = witness_element[0]
                tag = witness_element[1 : 1 + push]
                witness_element = witness_element[1 + push :]
            elif witness_element[0] == constants.OP_PUSHDATA1:
                push = witness_element[1]
                tag = witness_element[2 : 2 + push]
                witness_element = witness_element[2 + push :]
            elif witness_element[0] == constants.OP_PUSHDATA2:
                push = int.from_bytes(witness_element[1:3], "little")
                tag = witness_element[3 : 3 + push]
                witness_element = witness_element[3 + push :]
            elif witness_element[0] == constants.OP_0:
                tag = b"\x00"
                witness_element = witness_element[1:]
            elif witness_element[0] == constants.OP_1:
                tag = b"\x01"
                witness_element = witness_element[1:]
            elif witness_element[0] == constants.OP_2:
                tag = b"\x02"
                witness_element = witness_element[1:]
            elif witness_element[0] == constants.OP_3:
                tag = b"\x03"
                witness_element = witness_element[1:]
            elif witness_element[0] == constants.OP_5:
                tag = b"\x05"
                witness_element = witness_element[1:]
            else:
                raise ValueError(
                    f"Invalid data push while parsing tag: {witness_element[0]}"
                )
            if tag == b"\x01":
                # content type
                push = witness_element[0]
                content_type = witness_element[1 : 1 + push].decode("utf8")
                witness_element = witness_element[1 + push :]
                inscription["content_type"] = content_type
            elif tag == b"\x00":
                # data
                data = b""
                while witness_element and witness_element[0] != 104:
                    if witness_element[0] in range(1, 0x4C):
                        push = witness_element[0]
                        data += witness_element[1 : 1 + push]
                        witness_element = witness_element[1 + push :]
                    elif witness_element[0] == 0x4C:  # OP_PUSHDATA1
                        push = witness_element[1]
                        data += witness_element[2 : 2 + push]
                        witness_element = witness_element[2 + push :]
                    elif witness_element[0] == 0x4D:  # OP_PUSHDATA2
                        push = int.from_bytes(witness_element[1:3], "little")
                        data += witness_element[3 : 3 + push]
                        witness_element = witness_element[3 + push :]
                    else:
                        raise ValueError(f"Invalid data push: {witness_element[0]}")
                inscription["data"] = data
            elif tag == b"\x0b":
                # delegate
                # parse txid and index
                push = witness_element[0]
                delegate = witness_element[1 : 1 + push]
                witness_element = witness_element[1 + push :]
                txid = delegate[:32][::-1].hex()
                index = int.from_bytes(delegate[32:], "little")
                inscription["delegate"] = f"{txid}i{index}"
            elif tag == b"\x05":
                # metadata
                metadata = b""
                if witness_element[0] in range(1, 0x4C):
                    push = witness_element[0]
                    metadata += witness_element[1 : 1 + push]
                    witness_element = witness_element[1 + push :]
                elif witness_element[0] == 0x4C:  # OP_PUSHDATA1
                    push = witness_element[1]
                    metadata += witness_element[2 : 2 + push]
                    witness_element = witness_element[2 + push :]
                elif witness_element[0] == 0x4D:  # OP_PUSHDATA2
                    push = int.from_bytes(witness_element[1:3], "little")
                    metadata += witness_element[3 : 3 + push]
                    witness_element = witness_element[3 + push :]
                else:
                    raise ValueError(f"Invalid data push: {witness_element[0]}")
                if inscription.get("metadata", None) is None:
                    inscription["metadata"] = metadata
                else:
                    inscription["metadata"] += metadata
            elif tag == b"\x02":
                # pointer
                push = witness_element[0]
                pointer = witness_element[1 : 1 + push]
                witness_element = witness_element[1 + push :]
                inscription["pointer"] = int.from_bytes(pointer, "little")
            elif tag == b"\x11":
                # properties
                properties = b""
                if witness_element[0] in range(1, 0x4C):
                    push = witness_element[0]
                    properties += witness_element[1 : 1 + push]
                    witness_element = witness_element[1 + push :]
                elif witness_element[0] == 0x4C:  # OP_PUSHDATA1
                    push = witness_element[1]
                    properties += witness_element[2 : 2 + push]
                    witness_element = witness_element[2 + push :]
                elif witness_element[0] == 0x4D:  # OP_PUSHDATA2
                    push = int.from_bytes(witness_element[1:3], "little")
                    properties += witness_element[3 : 3 + push]
                    witness_element = witness_element[3 + push :]
                else:
                    raise ValueError(f"Invalid data push: {witness_element[0]}")
                if inscription.get("properties", None) is None:
                    inscription["properties"] = properties
                else:
                    inscription["properties"] += properties
            elif tag == b"\x03":
                # provenance
                # parse txid
                push = witness_element[0]
                provenance = witness_element[1 : 1 + push]
                witness_element = witness_element[1 + push :]
                txid = provenance[:32][::-1].hex()
                index = int.from_bytes(provenance[32:], "little")
                inscription["provenance"] = f"{txid}i{index}"
            else:
                raise ValueError(f"Unexpected tag: {tag}")
        inscriptions.append(inscription)

        ord_envelope_begin = witness_element.find(b"\x00\x63\x03ord")

    return inscriptions
