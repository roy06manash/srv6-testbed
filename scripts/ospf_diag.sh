#!/usr/bin/env bash
# Why is ospf6d not running our configuration on r1? (run after ospf_up.sh, as root)
echo "--- processes"
pgrep -af 'frr/(zebra|ospf6d)' | head
echo "--- /var/run/frr/r1"
ls -la /var/run/frr/r1
echo "--- r1 ospf6d.conf as written"
cat /etc/frr/r1/ospf6d.conf
echo "--- configuration check (dry run)"
ip netns exec r1 /usr/lib/frr/ospf6d -N r1 -u root -g root -f /etc/frr/r1/ospf6d.conf -C 2>&1 | head -20
echo "--- ospf6d log (tail)"
tail -15 /var/log/frr/r1-ospf6d.log 2>&1
