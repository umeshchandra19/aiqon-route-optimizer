# Recommendations and explanations for all shipments

## S001

```
Shipment S001: Shenzhen → Hamburg | perishable | 9.1 t | cargo value $87,000 | deadline 24 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S001-R4 [rail] SZX → HAM
  cost $4,537 (5.2% of cargo value) | expected transit 19.1 d (P90 20.5 d) | delay probability 11% | P(on-time) 98% | risk index 0.56 | score 70/100

Why this route:
  - Versus the cheapest allowed alternative (S001-R2, Air), it arrives 17 days later, raises delay probability from 4% to 11% and carries higher congestion/geopolitical risk (0.56 vs 0.25), but saves $28,919 (86%).
  - Deciding factor over the runner-up: freight cost (freight is 38% of cargo value ($33,456) vs 5.2% for the pick).

Alternatives not selected:
  - S001-R1 (Suez / Red Sea, $1,846, 36 d): excluded - only a <1% chance of on-time arrival (need 85%)
  - S001-R2 (Air, $33,456, 2 d): lower overall score (55 vs 70); main drawback: freight is 38% of cargo value ($33,456) vs 5.2% for the pick
  - S001-R3 (Panama, $2,433, 43 d): excluded - only a <1% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 94% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 14.4 score points.
```

## S002

```
Shipment S002: Singapore → New York / New Jersey | perishable | 6.4 t | cargo value $81,800 | deadline 48 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S002-R3 [sea → sea] SIN → PAN → NYC
  cost $1,634 (2.0% of cargo value) | expected transit 33.9 d (P90 36.1 d) | delay probability 17% | P(on-time) 100% | risk index 0.22 | score 85/100

Why this route:
  - Versus the cheapest allowed alternative (S002-R1, Suez / Red Sea), it arrives 3 days earlier, cuts delay probability from 31% to 17% and carries lower congestion/geopolitical risk (0.22 vs 0.58).
  - Versus the fastest allowed alternative (S002-R2, Air), it arrives 31 days later and raises delay probability from 5% to 17%, but saves $24,136 (94%).
  - Deciding factor over the runner-up: delay probability (31% delay probability vs 17% for the pick).

Alternatives not selected:
  - S002-R1 (Suez / Red Sea, $1,500, 36 d): lower overall score (71 vs 85); main drawback: 31% delay probability vs 17% for the pick
  - S002-R2 (Air, $25,770, 3 d): lower overall score (56 vs 85); main drawback: freight is 32% of cargo value ($25,770) vs 2.0% for the pick
  - S002-R4 (Cape of Good Hope, $1,992, 48 d): excluded - only a 62% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 97% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 14.9 score points.
```

## S003

```
Shipment S003: Singapore → Hamburg | standard | 31.1 t | cargo value $142,300 | deadline 44 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S003-R1 [sea → sea → sea] SIN → SUZ → PIR → HAM
  cost $4,525 (3.2% of cargo value) | expected transit 29.6 d (P90 31.9 d) | delay probability 26% | P(on-time) 100% | risk index 0.58 | score 75/100

Why this route:
  - Versus the cheapest allowed alternative (S003-R2, Air), it arrives 27 days later, raises delay probability from 5% to 26% and carries higher congestion/geopolitical risk (0.58 vs 0.14), but saves $92,414 (95%).
  - Deciding factor over the runner-up: freight cost (freight is 68% of cargo value ($96,939) vs 3.2% for the pick).

Alternatives not selected:
  - S003-R2 (Air, $96,939, 2 d): lower overall score (51 vs 75); main drawback: freight is 68% of cargo value ($96,939) vs 3.2% for the pick
  - S003-R3 (Panama, $8,095, 46 d): excluded - only a 23% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 98% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 23.6 score points.
```

## S004

```
Shipment S004: Shanghai → New York / New Jersey | urgent | 12.1 t | cargo value $623,300 | deadline 15 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S004-R2 [air] SHA → NYC
  cost $38,693 (6.2% of cargo value) | expected transit 2.1 d (P90 2.2 d) | delay probability 6% | P(on-time) 100% | risk index 0.17 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S004-R1 (Panama, $2,345, 30 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S004-R3 (Cape of Good Hope, $3,275, 47 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S005

```
Shipment S005: Shenzhen → Hamburg | standard | 11.1 t | cargo value $70,100 | deadline 49 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S005-R1 [sea → sea → sea → sea] SZX → SIN → SUZ → PIR → HAM
  cost $2,275 (3.2% of cargo value) | expected transit 37.6 d (P90 40.0 d) | delay probability 32% | P(on-time) 100% | risk index 0.59 | score 67/100

Why this route:
  - Versus the cheapest allowed alternative (S005-R3, Panama), it raises delay probability from 19% to 32% and carries higher congestion/geopolitical risk (0.59 vs 0.23), but saves $399 (15%) and arrives 8 days earlier.
  - Versus the fastest allowed alternative (S005-R2, Air), it arrives 36 days later, raises delay probability from 3% to 32% and carries higher congestion/geopolitical risk (0.59 vs 0.25), but saves $36,060 (94%).
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 92% of the 49-day deadline vs 77% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S005-R2 (Air, $38,334, 2 d): lower overall score (51 vs 67); main drawback: freight is 55% of cargo value ($38,334) vs 3.2% for the pick
  - S005-R3 (Panama, $2,673, 45 d): lower overall score (64 vs 67); main drawback: expected arrival uses 92% of the 49-day deadline vs 77% for the pick, so the schedule buffer is thinner

Confidence: Medium - the same route wins in 57% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 2.8 score points.
```

## S006

```
Shipment S006: Singapore → Los Angeles / Long Beach | high_value | 14.2 t | cargo value $906,400 | deadline 30 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S006-R1 [sea] SIN → LAX
  cost $2,141 (0.2% of cargo value) | expected transit 18.6 d (P90 20.1 d) | delay probability 17% | P(on-time) 100% | risk index 0.34 | score 88/100

Why this route:
  - Versus the cheapest allowed alternative (S006-R5, Transpacific / US land-bridge), it arrives 5 days earlier and cuts delay probability from 28% to 17%.
  - Versus the fastest allowed alternative (S006-R2, Air), it arrives 16 days later, raises delay probability from 8% to 17% and carries higher congestion/geopolitical risk (0.34 vs 0.21), but saves $44,874 (95%).
  - Versus the runner-up (S006-R4, Transpacific / US land-bridge), it arrives 4 days earlier and cuts delay probability from 21% to 17%.
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 75% of the 30-day deadline vs 62% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S006-R2 (Air, $47,015, 3 d): lower overall score (78 vs 88); main drawback: freight is 5.2% of cargo value ($47,015) vs 0.2% for the pick
  - S006-R3 (Cape of Good Hope, $5,523, 47 d): excluded - only a <1% chance of on-time arrival (need 80%)
  - S006-R4 (Transpacific / US land-bridge, $2,642, 22 d): lower overall score (87 vs 88); main drawback: expected arrival uses 75% of the 30-day deadline vs 62% for the pick, so the schedule buffer is thinner
  - S006-R5 (Transpacific / US land-bridge, $2,528, 24 d): lower overall score (84 vs 88); main drawback: 28% delay probability vs 17% for the pick

Confidence: Medium - the same route wins in 65% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 1.6 score points.
```

## S007

```
Shipment S007: Singapore → Rotterdam | standard | 5.0 t | cargo value $20,800 | deadline 37 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S007-R1 [sea → sea] SIN → SUZ → RTM
  cost $773 (3.7% of cargo value) | expected transit 25.2 d (P90 27.4 d) | delay probability 25% | P(on-time) 100% | risk index 0.53 | score 75/100

Why this route:
  - Versus the cheapest allowed alternative (S007-R5, Suez / Red Sea), it saves $166 (18%), arrives 6 days earlier and cuts delay probability from 29% to 25%.
  - Versus the fastest allowed alternative (S007-R2, Air), it arrives 23 days later, raises delay probability from 5% to 25% and carries higher congestion/geopolitical risk (0.53 vs 0.18), but saves $16,322 (95%).
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 84% of the 37-day deadline vs 68% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S007-R2 (Air, $17,095, 2 d): lower overall score (51 vs 75); main drawback: freight is 82% of cargo value ($17,095) vs 3.7% for the pick
  - S007-R3 (Panama, $1,238, 42 d): excluded - only a <1% chance of on-time arrival (need 70%)
  - S007-R4 (Cape of Good Hope, $1,181, 36 d): lower overall score (55 vs 75); main drawback: expected arrival uses 97% of the 37-day deadline vs 68% for the pick, so the schedule buffer is thinner
  - S007-R5 (Suez / Red Sea, $939, 31 d): dominated by S007-R1 (no better on any criterion)

Confidence: High - the same route wins in 96% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 14.1 score points.
```

## S008

```
Shipment S008: Nhava Sheva (Mumbai) → Rotterdam | standard | 6.6 t | cargo value $31,100 | deadline 36 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S008-R1 [sea → sea] NSA → SUZ → RTM
  cost $942 (3.0% of cargo value) | expected transit 20.9 d (P90 22.6 d) | delay probability 25% | P(on-time) 100% | risk index 0.53 | score 77/100

Why this route:
  - Versus the cheapest allowed alternative (S008-R2, Air), it arrives 19 days later, raises delay probability from 8% to 25% and carries higher congestion/geopolitical risk (0.53 vs 0.21), but saves $23,308 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 78% of cargo value ($24,249) vs 3.0% for the pick).

Alternatives not selected:
  - S008-R2 (Air, $24,249, 2 d): lower overall score (49 vs 77); main drawback: freight is 78% of cargo value ($24,249) vs 3.0% for the pick
  - S008-R3 (Panama, $2,309, 52 d): excluded - only a <1% chance of on-time arrival (need 70%)
  - S008-R4 (Cape of Good Hope, $2,144, 48 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 27.3 score points.
```

## S009

```
Shipment S009: Shenzhen → Rotterdam | standard | 12.5 t | cargo value $72,600 | deadline 41 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S009-R1 [sea → sea → sea] SZX → SIN → SUZ → RTM
  cost $2,090 (2.9% of cargo value) | expected transit 32.1 d (P90 34.3 d) | delay probability 30% | P(on-time) 99% | risk index 0.63 | score 67/100

Why this route:
  - Versus the cheapest allowed alternative (S009-R5, Suez / Red Sea), it saves $335 (14%) and arrives 2 days earlier.
  - Versus the fastest allowed alternative (S009-R2, Air), it arrives 30 days later, raises delay probability from 3% to 30% and carries higher congestion/geopolitical risk (0.63 vs 0.16), but saves $31,663 (94%).
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 83% of the 41-day deadline vs 78% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S009-R2 (Air, $33,752, 2 d): lower overall score (52 vs 67); main drawback: freight is 46% of cargo value ($33,752) vs 2.9% for the pick
  - S009-R3 (Panama, $2,365, 41 d): excluded - only a 44% chance of on-time arrival (need 70%)
  - S009-R4 (Cape of Good Hope, $3,022, 44 d): excluded - only a 2% chance of on-time arrival (need 70%)
  - S009-R5 (Suez / Red Sea, $2,425, 34 d): lower overall score (65 vs 67); main drawback: expected arrival uses 83% of the 41-day deadline vs 78% for the pick, so the schedule buffer is thinner

Confidence: Medium - the same route wins in 57% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 2.7 score points.
```

## S010

```
Shipment S010: Singapore → Rotterdam | perishable | 27.8 t | cargo value $439,500 | deadline 32 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S010-R1 [sea → sea] SIN → SUZ → RTM
  cost $4,066 (0.9% of cargo value) | expected transit 24.2 d (P90 25.6 d) | delay probability 18% | P(on-time) 99% | risk index 0.62 | score 78/100

Why this route:
  - Versus the cheapest allowed alternative (S010-R2, Air), it arrives 22 days later, raises delay probability from 4% to 18% and carries higher congestion/geopolitical risk (0.62 vs 0.24), but saves $100,773 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 24% of cargo value ($104,839) vs 0.9% for the pick).

Alternatives not selected:
  - S010-R2 (Air, $104,839, 2 d): lower overall score (55 vs 78); main drawback: freight is 24% of cargo value ($104,839) vs 0.9% for the pick
  - S010-R3 (Cape of Good Hope, $6,614, 35 d): excluded - only a <1% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 99% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 22.8 score points.
```

## S011

```
Shipment S011: Shanghai → Hamburg | standard | 9.2 t | cargo value $85,300 | deadline 33 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S011-R4 [rail] SHA → HAM
  cost $4,448 (5.2% of cargo value) | expected transit 18.5 d (P90 19.9 d) | delay probability 12% | P(on-time) 100% | risk index 0.57 | score 77/100

Why this route:
  - Versus the cheapest allowed alternative (S011-R2, Air), it arrives 16 days later, raises delay probability from 7% to 12% and carries higher congestion/geopolitical risk (0.57 vs 0.18), but saves $23,561 (84%).
  - Deciding factor over the runner-up: freight cost (freight is 33% of cargo value ($28,009) vs 5.2% for the pick).

Alternatives not selected:
  - S011-R1 (Suez / Red Sea, $1,890, 39 d): excluded - only a <1% chance of on-time arrival (need 70%)
  - S011-R2 (Air, $28,009, 2 d): lower overall score (50 vs 77); main drawback: freight is 33% of cargo value ($28,009) vs 5.2% for the pick
  - S011-R3 (Panama, $2,261, 44 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 26.8 score points.
```

## S012

```
Shipment S012: Nhava Sheva (Mumbai) → Los Angeles / Long Beach | urgent | 7.1 t | cargo value $246,400 | deadline 15 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S012-R2 [air] NSA → LAX
  cost $27,040 (11% of cargo value) | expected transit 3.2 d (P90 3.4 d) | delay probability 8% | P(on-time) 100% | risk index 0.21 | score 88/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S012-R1 (Transpacific / US land-bridge, $1,467, 29 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S012-R3 (Transpacific / US land-bridge, $1,722, 34 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S013

```
Shipment S013: Shanghai → New York / New Jersey | standard | 3.8 t | cargo value $36,100 | deadline 44 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S013-R1 [sea → sea] SHA → PAN → NYC
  cost $692 (1.9% of cargo value) | expected transit 30.6 d (P90 32.6 d) | delay probability 17% | P(on-time) 100% | risk index 0.21 | score 86/100

Why this route:
  - Versus the cheapest allowed alternative (S013-R2, Air), it arrives 29 days later and raises delay probability from 5% to 17%, but saves $11,657 (94%).
  - Deciding factor over the runner-up: freight cost (freight is 34% of cargo value ($12,348) vs 1.9% for the pick).

Alternatives not selected:
  - S013-R2 (Air, $12,348, 2 d): lower overall score (50 vs 86); main drawback: freight is 34% of cargo value ($12,348) vs 1.9% for the pick
  - S013-R3 (Cape of Good Hope, $1,485, 74 d): excluded - only a <1% chance of on-time arrival (need 70%)
  - S013-R4 (Cape of Good Hope, $1,065, 46 d): excluded - only a 7% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 36.3 score points.
```

## S014

```
Shipment S014: Shenzhen → Los Angeles / Long Beach | standard | 15.9 t | cargo value $88,500 | deadline 28 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S014-R1 [sea] SZX → LAX
  cost $1,819 (2.1% of cargo value) | expected transit 15.9 d (P90 17.2 d) | delay probability 16% | P(on-time) 99% | risk index 0.29 | score 85/100

Why this route:
  - Versus the cheapest allowed alternative (S014-R2, Air), it arrives 14 days later, raises delay probability from 5% to 16% and carries higher congestion/geopolitical risk (0.29 vs 0.13), but saves $42,762 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 50% of cargo value ($44,582) vs 2.1% for the pick).

Alternatives not selected:
  - S014-R2 (Air, $44,582, 2 d): lower overall score (52 vs 85); main drawback: freight is 50% of cargo value ($44,582) vs 2.1% for the pick
  - S014-R3 (Panama, $6,219, 50 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 33.9 score points.
```

## S015

```
Shipment S015: Shenzhen → Rotterdam | urgent | 24.4 t | cargo value $928,800 | deadline 26 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S015-R2 [air] SZX → RTM
  cost $93,135 (10% of cargo value) | expected transit 2.1 d (P90 2.2 d) | delay probability 4% | P(on-time) 100% | risk index 0.17 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S015-R1 (Suez / Red Sea, $5,062, 30 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S015-R3 (Panama, $5,995, 40 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S016

```
Shipment S016: Shenzhen → New York / New Jersey | standard | 4.9 t | cargo value $47,800 | deadline 41 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S016-R1 [sea → sea] SZX → PAN → NYC
  cost $1,104 (2.3% of cargo value) | expected transit 30.7 d (P90 32.7 d) | delay probability 18% | P(on-time) 100% | risk index 0.23 | score 81/100

Why this route:
  - Versus the cheapest allowed alternative (S016-R4, Transpacific / US land-bridge), it saves $733 (40%), arrives 4 days earlier, cuts delay probability from 28% to 18% and carries lower congestion/geopolitical risk (0.23 vs 0.31).
  - Versus the fastest allowed alternative (S016-R2, Air), it arrives 28 days later and raises delay probability from 4% to 18%, but saves $18,121 (94%).
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 84% of the 41-day deadline vs 75% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S016-R2 (Air, $19,225, 2 d): lower overall score (50 vs 81); main drawback: freight is 40% of cargo value ($19,225) vs 2.3% for the pick
  - S016-R3 (Cape of Good Hope, $1,531, 45 d): excluded - only a 1% chance of on-time arrival (need 70%)
  - S016-R4 (Transpacific / US land-bridge, $1,837, 34 d): dominated by S016-R1 (no better on any criterion)

Confidence: High - the same route wins in 98% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 15.4 score points.
```

## S017

```
Shipment S017: Singapore → Hamburg | perishable | 28.5 t | cargo value $524,300 | deadline 36 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S017-R4 [sea → rail] SIN → SHA → HAM
  cost $14,567 (2.8% of cargo value) | expected transit 27.5 d (P90 29.2 d) | delay probability 17% | P(on-time) 98% | risk index 0.53 | score 75/100

Why this route:
  - Versus the cheapest allowed alternative (S017-R1, Suez / Red Sea), it costs $10,357 more (3x the price), but arrives 4 days earlier, cuts delay probability from 31% to 17% and carries lower congestion/geopolitical risk (0.53 vs 0.65).
  - Versus the fastest allowed alternative (S017-R2, Air), it arrives 25 days later, raises delay probability from 4% to 17% and carries higher congestion/geopolitical risk (0.53 vs 0.21), but saves $71,434 (83%).
  - Deciding factor over the runner-up: freight cost (freight is 16% of cargo value ($86,000) vs 2.8% for the pick).

Alternatives not selected:
  - S017-R1 (Suez / Red Sea, $4,209, 32 d): lower overall score (61 vs 75); main drawback: expected arrival uses 89% of the 36-day deadline vs 76% for the pick, so the schedule buffer is thinner
  - S017-R2 (Air, $86,000, 2 d): lower overall score (63 vs 75); main drawback: freight is 16% of cargo value ($86,000) vs 2.8% for the pick
  - S017-R3 (Cape of Good Hope, $6,722, 41 d): excluded - only a <1% chance of on-time arrival (need 85%)
  - S017-R5 (Suez / Red Sea, $7,498, 52 d): excluded - only a <1% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 84% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 12.3 score points.
```

## S018

```
Shipment S018: Shenzhen → Hamburg | urgent | 16.5 t | cargo value $691,900 | deadline 16 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S018-R2 [air] SZX → HAM
  cost $62,189 (9.0% of cargo value) | expected transit 2.1 d (P90 2.3 d) | delay probability 6% | P(on-time) 100% | risk index 0.18 | score 90/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S018-R1 (Suez / Red Sea, $3,520, 36 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S018-R3 (Panama, $4,524, 45 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S018-R4 (Eurasia rail, $8,299, 19 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S019

```
Shipment S019: Shanghai → Rotterdam | standard | 9.5 t | cargo value $58,400 | deadline 41 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S019-R3 [sea → sea] SHA → PAN → RTM
  cost $2,315 (4.0% of cargo value) | expected transit 36.9 d (P90 39.1 d) | delay probability 22% | P(on-time) 96% | risk index 0.21 | score 64/100

Why this route:
  - Versus the cheapest allowed alternative (S019-R1, Suez / Red Sea), it costs $353 more (+18%) and arrives 3 days later, but cuts delay probability from 33% to 22% and carries lower congestion/geopolitical risk (0.21 vs 0.58).
  - Versus the fastest allowed alternative (S019-R2, Air), it arrives 35 days later and raises delay probability from 5% to 22%, but saves $35,549 (94%).
  - Versus the runner-up (S019-R4, Eurasia rail), it arrives 13 days later and raises delay probability from 17% to 22%, but saves $3,551 (61%) and carries lower congestion/geopolitical risk (0.21 vs 0.54).
  - Deciding factor over the runner-up: freight cost (freight is 10% of cargo value ($5,866) vs 4.0% for the pick).

Alternatives not selected:
  - S019-R1 (Suez / Red Sea, $1,962, 34 d): lower overall score (62 vs 64); main drawback: 33% delay probability vs 22% for the pick
  - S019-R2 (Air, $37,863, 2 d): lower overall score (50 vs 64); main drawback: freight is 65% of cargo value ($37,863) vs 4.0% for the pick
  - S019-R4 (Eurasia rail, $5,866, 24 d): lower overall score (64 vs 64); main drawback: freight is 10% of cargo value ($5,866) vs 4.0% for the pick
  - S019-R5 (Cape of Good Hope, $4,016, 67 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: Low - the same route wins in 45% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 0.2 score points.
```

## S020

```
Shipment S020: Nhava Sheva (Mumbai) → Hamburg | perishable | 12.7 t | cargo value $159,700 | deadline 29 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S020-R1 [sea → sea → sea] NSA → SUZ → PIR → HAM
  cost $2,147 (1.3% of cargo value) | expected transit 27.4 d (P90 29.8 d) | delay probability 29% | P(on-time) 87% | risk index 0.60 | score 56/100

Why this route:
  - Versus the cheapest allowed alternative (S020-R2, Air), it arrives 25 days later, raises delay probability from 4% to 29%, lowers on-time probability from >99% to 87% and carries higher congestion/geopolitical risk (0.60 vs 0.21), but saves $48,868 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 32% of cargo value ($51,015) vs 1.3% for the pick).
  - Hard rules changed the outcome: ignoring them, S020-R4 (Cape of Good Hope) would rank first, but it was ruled out (only a <1% chance of on-time arrival (need 85%)). The rules add $-2,016 (-1.3% of cargo value) to freight.

Alternatives not selected:
  - S020-R2 (Air, $51,015, 2 d): lower overall score (56 vs 56); main drawback: freight is 32% of cargo value ($51,015) vs 1.3% for the pick
  - S020-R3 (Cape of Good Hope, $3,588, 42 d): excluded - only a <1% chance of on-time arrival (need 85%)
  - S020-R4 (Cape of Good Hope, $4,163, 52 d): excluded - only a <1% chance of on-time arrival (need 85%)
  - S020-R5 (Suez / Red Sea, $2,766, 32 d): excluded - only a 2% chance of on-time arrival (need 85%)

Confidence: Medium - the same route wins in 57% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 0.2 score points.
```

## S021

```
Shipment S021: Nhava Sheva (Mumbai) → Hamburg | urgent | 34.0 t | cargo value $1,689,300 | deadline 15 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S021-R2 [air] NSA → HAM
  cost $103,231 (6.1% of cargo value) | expected transit 2.4 d (P90 2.5 d) | delay probability 6% | P(on-time) 100% | risk index 0.19 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S021-R1 (Suez / Red Sea, $4,675, 26 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S021-R3 (Cape of Good Hope, $7,987, 39 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S022

```
Shipment S022: Shenzhen → Los Angeles / Long Beach | standard | 16.8 t | cargo value $113,200 | deadline 24 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S022-R1 [sea] SZX → LAX
  cost $2,218 (2.0% of cargo value) | expected transit 14.4 d (P90 15.5 d) | delay probability 16% | P(on-time) 99% | risk index 0.40 | score 84/100

Why this route:
  - Versus the cheapest allowed alternative (S022-R2, Air), it arrives 13 days later, raises delay probability from 5% to 16% and carries higher congestion/geopolitical risk (0.40 vs 0.19), but saves $50,965 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 47% of cargo value ($53,183) vs 2.0% for the pick).

Alternatives not selected:
  - S022-R2 (Air, $53,183, 2 d): lower overall score (51 vs 84); main drawback: freight is 47% of cargo value ($53,183) vs 2.0% for the pick
  - S022-R3 (Panama, $7,665, 60 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 33.4 score points.
```

## S023

```
Shipment S023: Shenzhen → Los Angeles / Long Beach | high_value | 13.4 t | cargo value $1,178,700 | deadline 22 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S023-R1 [sea] SZX → LAX
  cost $1,506 (0.1% of cargo value) | expected transit 15.7 d (P90 16.9 d) | delay probability 13% | P(on-time) 99% | risk index 0.39 | score 88/100

Why this route:
  - Versus the cheapest allowed alternative (S023-R2, Air), it arrives 14 days later, raises delay probability from 4% to 13% and carries higher congestion/geopolitical risk (0.39 vs 0.26), but saves $33,506 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 3.0% of cargo value ($35,012) vs 0.1% for the pick).

Alternatives not selected:
  - S023-R2 (Air, $35,012, 2 d): lower overall score (84 vs 88); main drawback: freight is 3.0% of cargo value ($35,012) vs 0.1% for the pick
  - S023-R3 (Panama, $4,080, 39 d): excluded - only a <1% chance of on-time arrival (need 80%)
  - S023-R4 (Transpacific / US land-bridge, $2,897, 31 d): excluded - only a <1% chance of on-time arrival (need 80%)
  - S023-R5 (Transpacific / US land-bridge, $2,433, 25 d): excluded - only a <1% chance of on-time arrival (need 80%)

Confidence: Medium - the same route wins in 76% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 3.5 score points.
```

## S024

```
Shipment S024: Shanghai → Rotterdam | high_value | 11.2 t | cargo value $779,400 | deadline 39 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S024-R2 [air] SHA → RTM
  cost $35,533 (4.6% of cargo value) | expected transit 2.1 d (P90 2.2 d) | delay probability 5% | P(on-time) 100% | risk index 0.20 | score 81/100

Why this route:
  - It is the only route that satisfies the hard constraints.
  - Hard rules changed the outcome: ignoring them, S024-R3 (Panama) would rank first, but it was ruled out (only a 46% chance of on-time arrival (need 80%)). The rules add $33,336 (4.3% of cargo value) to freight.

Alternatives not selected:
  - S024-R1 (Suez / Red Sea, $1,988, 34 d): excluded - geopolitical exposure 0.79 exceeds cap 0.50
  - S024-R3 (Panama, $2,197, 39 d): excluded - only a 46% chance of on-time arrival (need 80%)
  - S024-R4 (Eurasia rail, $5,587, 22 d): excluded - geopolitical exposure 0.50 exceeds cap 0.50

Confidence: High (only feasible option).
```

## S025

```
Shipment S025: Nhava Sheva (Mumbai) → Rotterdam | urgent | 9.4 t | cargo value $421,200 | deadline 14 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S025-R2 [air] NSA → RTM
  cost $31,919 (7.6% of cargo value) | expected transit 2.1 d (P90 2.2 d) | delay probability 6% | P(on-time) 100% | risk index 0.16 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S025-R1 (Suez / Red Sea, $1,315, 22 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S025-R3 (Cape of Good Hope, $2,049, 37 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S025-R4 (Suez / Red Sea, $1,897, 32 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S026

```
Shipment S026: Nhava Sheva (Mumbai) → Los Angeles / Long Beach | standard | 25.0 t | cargo value $116,600 | deadline 42 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S026-R1 [sea → sea] NSA → SIN → LAX
  cost $4,634 (4.0% of cargo value) | expected transit 28.1 d (P90 29.9 d) | delay probability 19% | P(on-time) 100% | risk index 0.27 | score 80/100

Why this route:
  - Versus the cheapest allowed alternative (S026-R2, Air), it arrives 25 days later, raises delay probability from 5% to 19% and carries higher congestion/geopolitical risk (0.27 vs 0.16), but saves $84,610 (95%).
  - Deciding factor over the runner-up: freight cost (freight is 77% of cargo value ($89,244) vs 4.0% for the pick).

Alternatives not selected:
  - S026-R2 (Air, $89,244, 3 d): lower overall score (51 vs 80); main drawback: freight is 77% of cargo value ($89,244) vs 4.0% for the pick
  - S026-R3 (Cape of Good Hope, $8,732, 47 d): excluded - only a <1% chance of on-time arrival (need 70%)
  - S026-R4 (Suez / Red Sea, $7,228, 49 d): excluded - only a <1% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 28.7 score points.
```

## S027

```
Shipment S027: Singapore → Los Angeles / Long Beach | urgent | 3.5 t | cargo value $115,600 | deadline 18 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S027-R2 [air] SIN → LAX
  cost $11,571 (10% of cargo value) | expected transit 2.4 d (P90 2.6 d) | delay probability 4% | P(on-time) 100% | risk index 0.13 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S027-R1 (Transpacific / US land-bridge, $501, 18 d): excluded - only a 60% chance of on-time arrival (need 90%)
  - S027-R3 (Panama, $1,747, 64 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S027-R4 (Transpacific / US land-bridge, $644, 25 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S027-R5 (Transpacific / US land-bridge, $703, 23 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S028

```
Shipment S028: Singapore → Los Angeles / Long Beach | urgent | 14.5 t | cargo value $559,700 | deadline 15 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S028-R2 [air] SIN → LAX
  cost $56,485 (10% of cargo value) | expected transit 2.7 d (P90 2.9 d) | delay probability 5% | P(on-time) 100% | risk index 0.13 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S028-R1 (Transpacific / US land-bridge, $2,318, 18 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S028-R3 (Cape of Good Hope, $6,160, 49 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S028-R4 (Transpacific / US land-bridge, $2,860, 22 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S029

```
Shipment S029: Nhava Sheva (Mumbai) → New York / New Jersey | urgent | 8.9 t | cargo value $460,800 | deadline 34 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S029-R2 [air] NSA → NYC
  cost $35,958 (7.8% of cargo value) | expected transit 2.8 d (P90 2.9 d) | delay probability 5% | P(on-time) 100% | risk index 0.21 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S029-R1 (Suez / Red Sea, $2,002, 34 d): excluded - only a 72% chance of on-time arrival (need 90%)
  - S029-R3 (Cape of Good Hope, $2,224, 39 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S029-R4 (Suez / Red Sea, $2,738, 47 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S029-R5 (Panama, $3,142, 48 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S030

```
Shipment S030: Nhava Sheva (Mumbai) → New York / New Jersey | standard | 13.0 t | cargo value $66,900 | deadline 55 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S030-R3 [sea → sea → sea] NSA → CMB → CPT → NYC
  cost $3,455 (5.2% of cargo value) | expected transit 37.8 d (P90 39.8 d) | delay probability 22% | P(on-time) 100% | risk index 0.21 | score 76/100

Why this route:
  - Versus the cheapest allowed alternative (S030-R1, Suez / Red Sea), it costs $438 more (+15%) and arrives 4 days later, but cuts delay probability from 35% to 22% and carries lower congestion/geopolitical risk (0.21 vs 0.58).
  - Versus the fastest allowed alternative (S030-R2, Air), it arrives 35 days later and raises delay probability from 6% to 22%, but saves $50,600 (94%).
  - Deciding factor over the runner-up: delay probability (35% delay probability vs 22% for the pick).

Alternatives not selected:
  - S030-R1 (Suez / Red Sea, $3,016, 34 d): lower overall score (68 vs 76); main drawback: 35% delay probability vs 22% for the pick
  - S030-R2 (Air, $54,054, 3 d): lower overall score (50 vs 76); main drawback: freight is 81% of cargo value ($54,054) vs 5.2% for the pick

Confidence: High - the same route wins in 85% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 8.0 score points.
```

## S031

```
Shipment S031: Nhava Sheva (Mumbai) → New York / New Jersey | urgent | 19.9 t | cargo value $918,900 | deadline 17 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S031-R2 [air] NSA → NYC
  cost $65,082 (7.1% of cargo value) | expected transit 2.8 d (P90 2.9 d) | delay probability 8% | P(on-time) 100% | risk index 0.18 | score 90/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S031-R1 (Suez / Red Sea, $3,957, 34 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S031-R3 (Panama, $5,298, 42 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S031-R4 (Cape of Good Hope, $4,169, 38 d): excluded - only a <1% chance of on-time arrival (need 90%)
  - S031-R5 (Panama, $6,336, 49 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S032

```
Shipment S032: Shanghai → Los Angeles / Long Beach | perishable | 18.6 t | cargo value $173,200 | deadline 19 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S032-R1 [sea] SHA → LAX
  cost $2,152 (1.2% of cargo value) | expected transit 14.8 d (P90 15.9 d) | delay probability 14% | P(on-time) 97% | risk index 0.37 | score 80/100

Why this route:
  - Versus the cheapest allowed alternative (S032-R2, Air), it arrives 13 days later, raises delay probability from 5% to 14% and carries higher congestion/geopolitical risk (0.37 vs 0.24), but saves $51,855 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 31% of cargo value ($54,007) vs 1.2% for the pick).

Alternatives not selected:
  - S032-R2 (Air, $54,007, 2 d): lower overall score (55 vs 80); main drawback: freight is 31% of cargo value ($54,007) vs 1.2% for the pick
  - S032-R3 (Panama, $7,326, 52 d): excluded - only a <1% chance of on-time arrival (need 85%)
  - S032-R4 (Transpacific / US land-bridge, $3,814, 29 d): excluded - only a <1% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 99% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 25.1 score points.
```

## S033

```
Shipment S033: Nhava Sheva (Mumbai) → Hamburg | urgent | 3.8 t | cargo value $158,700 | deadline 26 days
Priorities (profile 'urgent'): cost 10%, time 50%, reliability 30%, risk 10%. Hard rules: P(on-time) ≥ 90%, geopolitical risk ≤ 0.90.

RECOMMENDED: S033-R2 [air] NSA → HAM
  cost $11,207 (7.1% of cargo value) | expected transit 2.3 d (P90 2.5 d) | delay probability 6% | P(on-time) 100% | risk index 0.19 | score 91/100

Why this route:
  - It is the only route that satisfies the hard constraints.

Alternatives not selected:
  - S033-R1 (Suez / Red Sea, $558, 27 d): excluded - only a 21% chance of on-time arrival (need 90%)
  - S033-R3 (Cape of Good Hope, $929, 42 d): excluded - only a <1% chance of on-time arrival (need 90%)

Confidence: High (only feasible option).
```

## S034

```
Shipment S034: Shenzhen → New York / New Jersey | high_value | 3.2 t | cargo value $432,700 | deadline 42 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S034-R1 [sea → sea] SZX → PAN → NYC
  cost $622 (0.1% of cargo value) | expected transit 31.2 d (P90 33.3 d) | delay probability 20% | P(on-time) 100% | risk index 0.27 | score 88/100

Why this route:
  - Versus the cheapest allowed alternative (S034-R2, Air), it arrives 29 days later and raises delay probability from 5% to 20%, but saves $10,290 (94%).
  - Deciding factor over the runner-up: freight cost (freight is 2.5% of cargo value ($10,912) vs 0.1% for the pick).

Alternatives not selected:
  - S034-R2 (Air, $10,912, 2 d): lower overall score (87 vs 88); main drawback: freight is 2.5% of cargo value ($10,912) vs 0.1% for the pick
  - S034-R3 (Eurasia rail, $1,731, 33 d): excluded - geopolitical exposure 0.61 exceeds cap 0.50
  - S034-R4 (Panama, $840, 41 d): excluded - only a 70% chance of on-time arrival (need 80%)
  - S034-R5 (Cape of Good Hope, $878, 45 d): excluded - only a 3% chance of on-time arrival (need 80%)

Confidence: Medium - the same route wins in 65% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 1.5 score points.
```

## S035

```
Shipment S035: Nhava Sheva (Mumbai) → Los Angeles / Long Beach | standard | 5.3 t | cargo value $27,000 | deadline 47 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S035-R1 [sea → sea] NSA → SIN → LAX
  cost $1,038 (3.8% of cargo value) | expected transit 28.9 d (P90 30.8 d) | delay probability 21% | P(on-time) 100% | risk index 0.23 | score 79/100

Why this route:
  - Versus the cheapest allowed alternative (S035-R2, Air), it arrives 26 days later, raises delay probability from 6% to 21% and carries higher congestion/geopolitical risk (0.23 vs 0.12), but saves $16,159 (94%).
  - Deciding factor over the runner-up: freight cost (freight is 64% of cargo value ($17,197) vs 3.8% for the pick).

Alternatives not selected:
  - S035-R2 (Air, $17,197, 3 d): lower overall score (51 vs 79); main drawback: freight is 64% of cargo value ($17,197) vs 3.8% for the pick
  - S035-R3 (Cape of Good Hope, $1,845, 47 d): excluded - only a 64% chance of on-time arrival (need 70%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 28.6 score points.
```

## S036

```
Shipment S036: Shenzhen → New York / New Jersey | standard | 13.1 t | cargo value $68,900 | deadline 49 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S036-R1 [sea → sea] SZX → PAN → NYC
  cost $2,894 (4.2% of cargo value) | expected transit 32.4 d (P90 34.6 d) | delay probability 21% | P(on-time) 100% | risk index 0.25 | score 79/100

Why this route:
  - Versus the cheapest allowed alternative (S036-R3, Eurasia rail), it raises delay probability from 18% to 21%, but saves $5,589 (66%) and carries lower congestion/geopolitical risk (0.25 vs 0.50).
  - Versus the fastest allowed alternative (S036-R2, Air), it arrives 30 days later and raises delay probability from 5% to 21%, but saves $49,661 (94%).
  - Deciding factor over the runner-up: freight cost (freight is 12% of cargo value ($8,482) vs 4.2% for the pick).

Alternatives not selected:
  - S036-R2 (Air, $52,555, 2 d): lower overall score (51 vs 79); main drawback: freight is 76% of cargo value ($52,555) vs 4.2% for the pick
  - S036-R3 (Eurasia rail, $8,482, 32 d): lower overall score (59 vs 79); main drawback: freight is 12% of cargo value ($8,482) vs 4.2% for the pick

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 19.7 score points.
```

## S037

```
Shipment S037: Shanghai → Los Angeles / Long Beach | high_value | 25.6 t | cargo value $1,453,200 | deadline 23 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S037-R1 [sea] SHA → LAX
  cost $2,904 (0.2% of cargo value) | expected transit 13.3 d (P90 14.2 d) | delay probability 13% | P(on-time) 100% | risk index 0.40 | score 88/100

Why this route:
  - Versus the cheapest allowed alternative (S037-R2, Air), it arrives 12 days later, raises delay probability from 6% to 13% and carries higher congestion/geopolitical risk (0.40 vs 0.23), but saves $70,692 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 5.1% of cargo value ($73,596) vs 0.2% for the pick).

Alternatives not selected:
  - S037-R2 (Air, $73,596, 2 d): lower overall score (78 vs 88); main drawback: freight is 5.1% of cargo value ($73,596) vs 0.2% for the pick
  - S037-R3 (Panama, $8,490, 39 d): excluded - only a <1% chance of on-time arrival (need 80%)
  - S037-R4 (Transpacific / US land-bridge, $5,436, 31 d): excluded - only a <1% chance of on-time arrival (need 80%)
  - S037-R5 (Transpacific / US land-bridge, $4,762, 28 d): excluded - only a <1% chance of on-time arrival (need 80%)

Confidence: High - the same route wins in 97% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 9.5 score points.
```

## S038

```
Shipment S038: Shanghai → Los Angeles / Long Beach | perishable | 15.8 t | cargo value $289,700 | deadline 20 days
Priorities (profile 'perishable'): cost 40%, time 26%, reliability 22%, risk 12%. Hard rules: P(on-time) ≥ 85%, geopolitical risk ≤ 0.90.

RECOMMENDED: S038-R1 [sea] SHA → LAX
  cost $1,968 (0.7% of cargo value) | expected transit 14.7 d (P90 15.7 d) | delay probability 11% | P(on-time) 98% | risk index 0.43 | score 86/100

Why this route:
  - Versus the cheapest allowed alternative (S038-R2, Air), it arrives 13 days later, raises delay probability from 4% to 11% and carries higher congestion/geopolitical risk (0.43 vs 0.22), but saves $48,865 (96%).
  - Deciding factor over the runner-up: freight cost (freight is 18% of cargo value ($50,833) vs 0.7% for the pick).

Alternatives not selected:
  - S038-R2 (Air, $50,833, 2 d): lower overall score (61 vs 86); main drawback: freight is 18% of cargo value ($50,833) vs 0.7% for the pick
  - S038-R3 (Panama, $7,043, 54 d): excluded - only a <1% chance of on-time arrival (need 85%)

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 25.2 score points.
```

## S039

```
Shipment S039: Shanghai → Rotterdam | high_value | 19.9 t | cargo value $846,300 | deadline 44 days
Priorities (profile 'high_value'): cost 60%, time 7%, reliability 12%, risk 21%. Hard rules: P(on-time) ≥ 80%, geopolitical risk ≤ 0.50.

RECOMMENDED: S039-R3 [sea → sea] SHA → PAN → RTM
  cost $3,946 (0.5% of cargo value) | expected transit 36.8 d (P90 38.8 d) | delay probability 16% | P(on-time) 99% | risk index 0.23 | score 87/100

Why this route:
  - Versus the cheapest allowed alternative (S039-R2, Air), it arrives 35 days later and raises delay probability from 4% to 16%, but saves $52,509 (93%).
  - Deciding factor over the runner-up: freight cost (freight is 6.7% of cargo value ($56,455) vs 0.5% for the pick).

Alternatives not selected:
  - S039-R1 (Suez / Red Sea, $3,456, 33 d): excluded - geopolitical exposure 0.71 exceeds cap 0.50
  - S039-R2 (Air, $56,455, 2 d): lower overall score (73 vs 87); main drawback: freight is 6.7% of cargo value ($56,455) vs 0.5% for the pick

Confidence: High - the same route wins in 100% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 14.3 score points.
```

## S040

```
Shipment S040: Singapore → Rotterdam | standard | 23.1 t | cargo value $193,800 | deadline 42 days
Priorities (profile 'standard'): cost 45%, time 22%, reliability 22%, risk 11%. Hard rules: P(on-time) ≥ 70%, geopolitical risk ≤ 0.90.

RECOMMENDED: S040-R1 [sea → sea] SIN → SUZ → RTM
  cost $2,863 (1.5% of cargo value) | expected transit 23.4 d (P90 25.0 d) | delay probability 26% | P(on-time) 100% | risk index 0.62 | score 78/100

Why this route:
  - Versus the cheapest allowed alternative (S040-R4, Cape of Good Hope), it raises delay probability from 22% to 26% and carries higher congestion/geopolitical risk (0.62 vs 0.16), but saves $1,831 (39%) and arrives 12 days earlier.
  - Versus the fastest allowed alternative (S040-R2, Air), it arrives 21 days later, raises delay probability from 5% to 26% and carries higher congestion/geopolitical risk (0.62 vs 0.21), but saves $70,685 (96%).
  - Deciding factor over the runner-up: deadline buffer (expected arrival uses 84% of the 42-day deadline vs 56% for the pick, so the schedule buffer is thinner).

Alternatives not selected:
  - S040-R2 (Air, $73,547, 2 d): lower overall score (51 vs 78); main drawback: freight is 38% of cargo value ($73,547) vs 1.5% for the pick
  - S040-R3 (Panama, $4,839, 39 d): lower overall score (70 vs 78); main drawback: expected arrival uses 92% of the 42-day deadline vs 56% for the pick, so the schedule buffer is thinner
  - S040-R4 (Cape of Good Hope, $4,694, 35 d): lower overall score (73 vs 78); main drawback: expected arrival uses 84% of the 42-day deadline vs 56% for the pick, so the schedule buffer is thinner

Confidence: Medium - the same route wins in 72% of what-if runs (cost ±10%, time ±8%, delay odds ±30%, risk ±0.10, weights jittered); margin over runner-up 5.1 score points.
```
