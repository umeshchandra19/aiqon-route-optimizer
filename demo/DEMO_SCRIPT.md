# 5-minute demo script

Screen-record a terminal (and optionally `report/Aiqon_Route_Optimization_Report.pdf` for the figures).
Run `demo/run_demo.sh` and talk over each step.

| Time | Step | What to say |
|---|---|---|
| 0:00 | Problem | Route choice is a decision under uncertainty: cheap routes are slow or risky, fast routes are expensive. I model that and explain the pick. |
| 0:30 | Step 1: data | Synthetic network of 13 hubs, 40 shipments, 157 options. Every shipment has real trade-offs by construction; there is also a hidden ground truth for evaluation. |
| 1:00 | Step 2: recommend | Read the output top to bottom: pick, why vs cheapest / fastest / runner-up, why each alternative was rejected, confidence. |
| 2:00 | Step 3: weights | The operator can change priorities; the pick and explanation change. |
| 2:30 | Step 4: sweep | Sensitivity of one decision: it flips to air only when the cost weight drops below ~0.22. |
| 3:00 | Steps 5-6: rules and scenario | Hard rules are non-compensatory; a Red Sea crisis shifts routing; when rules force an expensive pick the system flags it for review. |
| 3:45 | Step 7: evaluation | Compare with cheapest / fastest / fixed weights / EV-cost against a hidden ground truth. Be honest that the EV baseline shares the yardstick's model. |
| 4:30 | Limitations | Synthetic data, static parameters, blunt hard rules; next step is learning delay distributions from real data. |
