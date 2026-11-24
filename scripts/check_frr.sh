#!/usr/bin/env bash
# What FRRouting is installed, and does it support per-namespace instances (--pathspace)?
dpkg -s frr 2>/dev/null | grep -E '^(Package|Version)'
for d in zebra ospf6d bfdd; do
  if [ -x /usr/lib/frr/$d ]; then echo "$d: $(/usr/lib/frr/$d --version 2>&1 | head -1)"; else echo "$d: MISSING"; fi
done
echo "--- zebra options"
/usr/lib/frr/zebra --help 2>&1 | grep -E -- 'pathspace|--user|--group|--daemon'
echo "--- vtysh options"
vtysh --help 2>&1 | grep -E -- 'pathspace|-N'
