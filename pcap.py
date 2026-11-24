"""Minimal pure-Python pcap + IPv6/SRH (RFC 8754) parser. No third-party dependencies."""
import ipaddress
import struct


def read_pcap(path):
    """Yield (ts_ns, orig_len, frame_bytes). Ethernet link type only."""
    data = open(path, "rb").read()
    magic = data[:4]
    if magic in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"):
        e = "<"
    elif magic in (b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"):
        e = ">"
    else:
        raise ValueError("not a classic pcap file: %s" % path)
    nano = magic in (b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d")
    _, _, _, _, _, network = struct.unpack(e + "HHiIII", data[4:24])
    if network != 1:
        raise ValueError("unsupported link type %d (need Ethernet)" % network)
    off = 24
    while off + 16 <= len(data):
        sec, frac, incl, orig = struct.unpack(e + "IIII", data[off:off + 16])
        off += 16
        frame = data[off:off + incl]
        off += incl
        yield sec * 10**9 + (frac if nano else frac * 1000), orig, frame


def _parse_ipv6(b):
    if len(b) < 40 or b[0] >> 4 != 6:
        return None
    info = {"dst": str(ipaddress.IPv6Address(b[24:40])), "srh": None, "inner": None, "dport": None}
    nh, off = b[6], 40
    while nh in (0, 43, 60):  # hop-by-hop, routing, destination options
        if len(b) < off + 8:
            return info
        nxt, hlen = b[off], (b[off + 1] + 1) * 8
        if nh == 43 and b[off + 2] == 4:  # routing type 4 = SRH
            nseg = b[off + 4] + 1
            segs = [str(ipaddress.IPv6Address(b[off + 8 + 16 * i: off + 24 + 16 * i]))
                    for i in range(nseg)]
            info["srh"] = {"sl": b[off + 3], "nseg": nseg, "segs": segs, "len": hlen}
        nh, off = nxt, off + hlen
    if nh == 41:
        info["inner"] = _parse_ipv6(b[off:])
    elif nh == 17 and len(b) >= off + 8:
        info["dport"] = int.from_bytes(b[off + 2:off + 4], "big")
    return info


def parse_frame(frame):
    if len(frame) < 54 or frame[12:14] != b"\x86\xdd":
        return None
    return _parse_ipv6(frame[14:])


def data_packet(info, h2, port):
    """Return the outer-info if this frame carries the measured flow (plain or SRv6-encapsulated)."""
    if info is None:
        return False
    final = info["inner"] if info.get("inner") else info
    return final is not None and final["dst"] == h2 and final.get("dport") == port
