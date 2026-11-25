# SRv6 path steering and failure recovery testbed

Five routers (Linux network namespaces), two explicit SRv6 paths and one link failure.
Compares plain IPv6 forwarding with an SRv6 policy under the same topology, detector and failure.
Results and analysis: `REPORT.md`. Topology and addressing: `topology.md`.

## Requirements

The testbed needs Linux (network namespaces, SRv6 in the kernel). On a Mac, use an Ubuntu VM:

    brew install --cask multipass
    multipass launch 24.04 --name srv6 --cpus 2 --memory 2G --disk 10G
    multipass mount ~/srv6-testbed srv6:/home/ubuntu/srv6-testbed
    multipass exec srv6 -- sudo apt-get update
    multipass exec srv6 -- sudo apt-get install -y iproute2 tcpdump python3 traceroute tshark

Then, inside the VM (`multipass shell srv6`), install the module that provides `tc netem`:

    sudo apt-get install -y linux-modules-extra-$(uname -r)

Edit files on the Mac; run everything in the VM. Inside the VM the folder is
/home/ubuntu/srv6-testbed. Python needs no extra packages.

## Run (inside the VM, as root)

    sudo scripts/setup.sh                       # build topology + SRv6 config
    sudo ip netns exec h1 ping -6 -c3 2001:db8:a5::2
    sudo python3 run_experiment.py --runs 20 --capture   # about 10 min
    sudo bash scripts/show_config.sh            # node configs -> results/config/
    python3 analyze.py results                  # -> results/summary.md, runs.csv
    python3 verify_sids.py results              # -> results/sid_traversal.md
    sudo bash scripts/path_demo.sh | tee results/path_demo.txt
    bash scripts/tshark_check.sh                # independent decode of the captures
    sudo scripts/teardown.sh

OSPFv3 baseline (needs `sudo apt-get install -y frr`, `sudo systemctl disable --now frr` and
`sudo usermod -aG frrvty root` once):

    sudo bash scripts/ospf_up.sh                # topology + OSPFv3, no static host routes
    sudo python3 ospf_experiment.py --runs 10   # ~5 min -> results_ospf/
    python3 scripts/patch_analyze.py            # once: lets analyze.py read runs without a detector
    python3 analyze.py results_ospf
    sudo scripts/teardown.sh                    # also stops the FRR daemons

Real BFD (FRR bfdd) registered with OSPFv3, silent failure:

    sudo bash scripts/bfd_up.sh                 # needs the overlay topology up
    sudo python3 overlay_bfd.py --runs 10       # ~12 min -> results_bfd/
    sudo python3 analyze.py results_bfd

Pre-computed local repair (TI-LFA-like, not TI-LFA), link-down failure:

    sudo python3 overlay_localrepair.py --runs 10   # ~9 min -> results_localrepair/
    # use tools/outage_summary.py (REPORT 4.8, 4.11); analyze.py cannot measure sub-jitter outages

Real link-down failure (needs the overlay topology up; adds a plain-OSPFv3 mode):

    sudo python3 overlay_linkdown.py --runs 10   # ~12 min -> results_linkdown/
    sudo python3 analyze.py results_linkdown

SRv6 over the OSPFv3 underlay:

    sudo bash scripts/overlay_up.sh             # OSPFv3 + locators advertised, SRv6 policy at r1
    sudo bash scripts/overlay_check.sh          # each policy must deliver traffic
    sudo python3 overlay_experiment.py --runs 10   # ~12 min -> results_overlay/
    python3 analyze.py results_overlay
    sudo scripts/teardown.sh

Real BFD on all five core links, remote-link failure, default OSPF timers (need the overlay topology up):

    sudo bash scripts/bfd_all.sh                          # 10 BFD sessions, prints "sessions up: 10 of 10"
    sudo python3 overlay_bfd.py --runs 10 --out results_bfd_all
    sudo python3 overlay_remote.py --r2r5-bfd on  --runs 10   # failure on r2-r5 -> results_remote_bfd/
    sudo python3 overlay_remote.py --r2r5-bfd off --runs 10   # same, BFD removed -> results_remote_nobfd/
    sudo python3 overlay_defaulttimers.py --runs 5        # hello 10 s / dead 40 s, ~15 min -> results_ospf_default/

Local-repair control without SRv6, header overhead, measurement checks:

    sudo python3 overlay_localrepair_plain.py --runs 10                 # 1,000 pps -> results_localrepair_plain/
    sudo python3 overlay_localrepair_plain.py --runs 10 --pps 5000 --out results_lrp_5k_v2
    sudo bash scripts/overhead_modes.sh                                 # frame sizes: plain, encap, encap.red
    python3 tools/outage_summary.py results_linkdown results_bfd_all    # interruption = largest loss-bearing gap
    python3 tools/gap_report.py results_linkdown                        # every gap over 10 ms, outage or stall

Plots (after `python3 analyze.py` on each results folder):

    sudo apt-get install -y python3-matplotlib   # once
    python3 plot_results.py                      # -> plots/

From the Mac, any of these can be run as `multipass exec srv6 -- sudo ...` with the full path
/home/ubuntu/srv6-testbed/....

## Files

- `scripts/setup.sh`, `teardown.sh`, `set_policy.sh`: topology, SIDs, the r1 policies
  (ipv6/srv6 x primary/backup)
- `scripts/ospf_up.sh`, `ospf_diag.sh`, `check_frr.sh`: OSPFv3 (FRRouting) bring-up and diagnostics
- `ospf_experiment.py`: repeated failures repaired by OSPF itself -> `results_ospf/`
- `scripts/show_config.sh`: dump every node's addresses, routes and sysctls
- `scripts/path_demo.sh`: traceroute, per-link counters, and the "no route on r3/r4" test
- `scripts/traceroute_diag*.sh`: why SRv6 hides transit hops in traceroute (hop-limit captures)
- `scripts/test_*.sh`, `diag.sh`, `tshark_check.sh`, `tools/gapprobe.py`: test and diagnostic helpers
- `tools/udp_sender.py`, `udp_receiver.py`: numbered UDP flow with timestamps
- `tools/echo_responder.py`, `detector.py`: liveness peer and the BFD-like detector + scripted repair
- `run_experiment.py`: repeated-failure driver (both modes, optional tcpdump captures)
- `pcap.py`, `verify_sids.py`: capture parser and SID-traversal / overhead verification
- `analyze.py`: loss, interruption, detection and repair statistics
- `results/`: final data, captures (`pcaps/`), configs
- `scripts/overlay_up.sh`, `set_overlay.sh`, `overlay_check.sh`, `overlay_experiment.py`: SRv6 over OSPFv3
- `overlay_linkdown.py`: same experiment with a real link-down failure
- `results_overlay/`: SRv6-over-OSPFv3 results (silent failure)
- `scripts/bfd_up.sh`, `overlay_bfd.py`, `results_bfd/`: real BFD + OSPFv3 experiment
- `scripts/mtr_check.sh`: mtr path view (output in `results/mtr.txt`)
- `overlay_localrepair.py`, `results_localrepair/`: local repair experiment (set_overlay.sh `protected` policy)
- `results_linkdown/`: link-down failure results
- `scripts/bfd_all.sh`, `results_bfd_all/`: real BFD on all five core links
- `overlay_remote.py`, `results_remote_bfd/`, `results_remote_nobfd/`: failure on the remote link r2-r5, BFD on or off
- `overlay_defaulttimers.py`, `results_ospf_default/`: OSPFv3 with hello 10 s / dead 40 s
- `overlay_localrepair_plain.py`, `results_localrepair_plain/`, `results_lrp_5k_v2/`: local repair with plain IPv6 routes (control); `results_lrp_5k_full/` is an earlier run kept as evidence
- `scripts/overhead_modes.sh`: measured frame size for plain, encap and encap.red
- `tools/outage_summary.py`, `tools/gap_report.py`, `tools/edge_loss.py`: interruption metric, gap and stall listing, start or end loss
- `plot_results.py`: box plots from every `runs.csv` -> `plots/*.png` (needs `python3-matplotlib`)
- `plots/`: generated figures (scripted IPv6 vs SRv6, all modes, detection vs repair)
- `results/config/frr/`: FRRouting configs and running configs, `environment.txt` has versions
- `results_20ms/`: scaling check with 20 ms probes

## Method in brief

- Failure: tc netem 100 % loss on r1-r2 (the link stays up, a silent failure).
- Detection: UDP prober on r1, 50 ms interval, 3 missed intervals since the last reply. Not real BFD.
  The UDP sender starts first so the VM stays awake (idle timers fire 60-95 ms late).
- Repair: the detector runs `set_policy.sh <mode>-backup`.
- Both modes use the same detector, failure and repair script; only the route at r1 differs.

## Known issues and limits

- SID routes must sit on a dummy interface (`sid0`), not `lo`, on this kernel.
- Timings include about 10 ms of VM scheduling jitter; detector timers below about 100 ms need
  the traffic running to be reliable in an idle VM.
- Results describe this testbed only, not an operational advantage of SRv6.
- TI-LFA is not implemented (FRRouting needs SR-MPLS and the VM kernel has none); real BFD is.
- Excluded runs and unexplained observations are listed in REPORT.md sections 4.9 to 4.12 and 5.
