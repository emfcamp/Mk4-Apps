"""Functions to sync the hardware clock to internet network time servers

Derived from the 2016 implementation.
"""

___license___ = "MIT"

import database
import usocket
import machine
import utime

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600
# With Mk3 Firmware an IP address string works 5%, hangs at socket.socket(..) 95%, could be a bug in 2016 upython?
NTP_HOSTS = ["ntp-gps.emf.camp", "0.emfbadge.pool.ntp.org", "1.emfbadge.pool.ntp.org", "2.emfbadge.pool.ntp.org", "3.emfbadge.pool.ntp.org"]
NTP_PORT = 123

def get_NTP_time():
        for NTP_HOST in NTP_HOSTS:
                res = query_NTP_host(NTP_HOST)
                if res is not None:
                        return res
        return None


def query_NTP_host(_NTP_HOST):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        # Catch exception when run on a network without working DNS
        try:
                addr = usocket.getaddrinfo(_NTP_HOST, NTP_PORT)[0][-1]
        except OSError:
                return None
        s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        s.sendto(NTP_QUERY, addr)

        # Setting timeout for receiving data. Because we're using UDP,
        # there's no need for a timeout on send.
        msg = None
        try:
                msg = s.recv(48)
        except OSError:
                pass
        finally:
                s.close()

        if msg is None:
                return None

        import struct

        stratum = int(msg[1])
        if stratum == 0:
                # KoD, reason doesn't matter, failover to next host
                return None

        val = struct.unpack("!I", msg[40:44])[0]

        print("Using NTP Host: %s, Stratum: %d" % (_NTP_HOST, stratum))
        return val - NTP_DELTA


def set_NTP_time():
        print("Setting time from NTP")

        t = get_NTP_time()
        if t is None:
                print("Could not set time from NTP")
                return False

        with database.Database() as db:
                tz = db.get("timezone", 1)

        tm = utime.localtime(t)
        tm = tm[0:3] + ((tm[3] + tz),) + tm[3:6]
        rtc = machine.RTC()
        rtc.init(tm)

        return True
