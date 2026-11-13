#!/usr/bin/env bash
# Walk-through for the (optional) <=5 minute demo. Run from the repo root.
set -e
pause() { read -r -p $'\n-- press Enter to continue --\n'; }

echo "### 1. The data: shipments and their route options"; python -m routeopt list | head -12
pause
echo "### 2. Recommend + explain one shipment (standard cargo)"; python -m routeopt recommend S007
pause
echo "### 3. Same shipment, operator changes priorities: cost matters little, speed a lot"
python -m routeopt recommend S007 --weights cost=0.1,time=0.5,reliability=0.3,risk=0.1 | sed -n '1,12p'
pause
echo "### 4. How close was the call?  Sweep the cost weight"; python -m routeopt recommend S007 --sweep cost | tail -6
pause
echo "### 5. Urgent cargo + a hard rule: no air freight allowed"
python -m routeopt recommend S004 --exclude-modes air | sed -n '1,18p'
pause
echo "### 6. Disruption: Red Sea crisis, high-value cargo"; python -m routeopt recommend S006 --scenario red_sea | sed -n '1,14p'
pause
echo "### 7. Evaluation against ground truth and baselines"; python -m routeopt evaluate | head -14
