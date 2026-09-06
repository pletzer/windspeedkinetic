# windspeedkinetic

A back-of-the-envelope, purely kinematic estimate of windsurfer speed as a
function of course angle, based on the sail's angle of attack.

## Setup

Wind vector **w** has `|w| = 1` and blows from the north. The board's
velocity **s** makes angle `phi` with the upwind direction, `0 < phi <= pi`,
with `phi = pi` meaning dead downwind. The apparent wind is

```
v_a = w - s
```

Let `beta` be the angle between `v_a` and the course **s**. The sail's angle
of attack `alpha` is the angle between `v_a` and the sail chord. Assuming the
chord lies along the course line, and that the apparent wind meets it almost
head-on for small `alpha` (airfoil-like flow), we take `beta = pi - alpha`
(not `beta = alpha`).

## Derivation

From the vector triangle `w = v_a + s` (sides `1`, `s`, `|v_a|`, with the
angle between `w` and `s` equal to `pi - phi`):

```
law of sines:   sin(beta) = sin(phi) / |v_a|
dot product:    cos(beta) = -(s + cos(phi)) / |v_a|
```

Setting `beta = pi - alpha` (so `sin(beta) = sin(alpha)`,
`cos(beta) = -cos(alpha)`) and eliminating `|v_a|` gives a closed form:

```
s(phi) = cot(alpha) * sin(phi) - cos(phi)
```

### Checks that fall out of the algebra

- `s(phi) = 0` exactly at `phi = alpha`: you can't point closer to the wind
  than the sail's angle of attack.
- `s(phi) = 1` exactly at `phi = pi` (dead downwind), for any `alpha` — a
  degenerate boundary point of the model, not a real prediction.
- The maximum speed has a closed form too:
  `phi_max = 90 deg + alpha`, `s_max = 1 / sin(alpha)` — always a broad
  reach, never dead downwind.

### Leeway

A fixed sail-trim offset `delta` from the course line is equivalent to
using an effective angle of attack `alpha_eff = alpha - delta`. Real
leeway (the board slipping sideways through the water, so the hull/rig
sits a few degrees to windward of the actual track) corresponds to
`delta = -leeway`, i.e. `alpha_eff = alpha + leeway`. This always
increases the effective angle of attack and so reduces `s(phi)` — leeway
is a pure speed penalty relative to the idealised, zero-slip curves.

### Caveat

This is pure kinematics: there is no drag or hull resistance, so speeds for
small `alpha` grow unrealistically large near a beam reach. A real speed
limit needs a force balance (sail lift/drag vs. board/water resistance),
not just the angle-matching condition used here.

## Usage

```bash
pip install numpy matplotlib
python3 windsurfer_speed.py
```

Produces `windsurfer_speed.png`: a Cartesian plot of `s/|w|` vs. course
angle `phi`, and a polar "sailing diagram" view (wind from the top, `phi`
increasing clockwise), for `alpha = 10, 20, 30, 40` degrees, solid curves
with no leeway and dashed curves with leeway added. Peak points are marked
on every curve. The script also prints a table of `(phi_max, s_max)` for
each case.
