"""
Windsurfer speed from a purely kinematic (angle-of-attack) argument.

Setup
-----
Wind vector w has |w| = 1, blowing from the north.
Board velocity s makes angle phi with the upwind direction (north),
with phi = pi meaning dead downwind (0 < phi <= pi).
Apparent wind: v_a = w - s.

Let beta be the angle between v_a and the course s. The sail's angle
of attack alpha is the angle between v_a and the sail chord; here we
assume the chord lies along the course and, since the apparent wind
meets the chord almost head-on for small alpha (airfoil-like flow),
we take beta = pi - alpha rather than beta = alpha.

Combining
    sin(beta) = sin(phi) / |v_a|          (law of sines, always true)
    beta = pi - alpha
with |v_a|^2 = 1 + s^2 + 2 s cos(phi)     (law of cosines)
gives a closed form for the equilibrium-free speed:

    s(phi) = cot(alpha) * sin(phi) - cos(phi)

Notes
-----
- s(phi) = 0 exactly at phi = alpha: the model predicts you cannot
  point closer to the wind than the sail's angle of attack.
- s(phi) = 1 exactly at phi = pi (dead downwind), for any alpha.
- This is pure kinematics: there is no drag or hull resistance, so
  speeds for small alpha grow unrealistically large near a beam
  reach. A real speed limit needs a force balance (sail lift/drag
  vs. board/water resistance).

Maximum of s(phi)
-----------------
ds/dphi = cot(alpha) cos(phi) + sin(phi) = 0  =>  tan(phi) = -cot(alpha),
whose solution in (alpha, pi) is

    phi_max = pi/2 + alpha        (i.e. 90 deg + alpha)
    s_max   = s(phi_max) = 1 / sin(alpha)

both in closed form -- no numerical root-finding needed.

Leeway
------
The formula above assumes the sail chord sits exactly along the
course line s (no trim offset). Allowing the chord to be offset from
the course by a fixed angle delta (positive = rotated toward the
leeward/downwind side) generalises the relation to

    beta = pi - alpha + delta  =>  s(phi) = cot(alpha - delta) sin(phi) - cos(phi)

i.e. a fixed offset delta is equivalent to using an effective angle
of attack alpha_eff = alpha - delta. Real leeway -- the board
slipping sideways through the water so the hull/rig sits a few
degrees to windward of the actual track -- corresponds to delta =
-LEEWAY_DEG (chord rotated toward the windward side), i.e.

    alpha_eff = alpha + LEEWAY_DEG

This always increases the effective angle of attack and so reduces
s(phi): leeway is a pure speed penalty relative to the idealised,
zero-slip curves.
"""

import numpy as np
import matplotlib.pyplot as plt


def s_of_phi(phi_rad, alpha_rad):
    """Kinematic windsurfer speed (in units of wind speed) vs course angle.

    phi_rad, alpha_rad : angle from the upwind direction (radians).
    Returns NaN where phi < alpha (not sailable at that angle of attack).
    """
    s = 1.0 / np.tan(alpha_rad) * np.sin(phi_rad) - np.cos(phi_rad)
    return np.where(phi_rad >= alpha_rad, s, np.nan)


def max_point(alpha_deg):
    """Closed-form (phi_max, s_max) for a given alpha, in degrees / speed units."""
    phi_max_deg = 90.0 + alpha_deg
    s_max = 1.0 / np.sin(np.radians(alpha_deg))
    return phi_max_deg, s_max


LEEWAY_DEG = 10.0
LEEWAY_ALPHAS_DEG = [20, 30, 40]  # the "likely" alpha range, with a leeway curve each


def main():
    alphas_deg = [10, 20, 30, 40]
    phi_deg = np.linspace(0, 180, 721)  # 0.25 degree steps
    phi_rad = np.radians(phi_deg)

    fig = plt.figure(figsize=(13, 6))
    ax = fig.add_subplot(1, 2, 1)
    axp = fig.add_subplot(1, 2, 2, projection="polar")
    # phi = 0 (upwind) at the top, increasing clockwise, like a compass bearing
    axp.set_theta_zero_location("N")
    axp.set_theta_direction(-1)

    print(f"{'alpha (deg)':>12} {'phi_max (deg)':>15} {'s_max':>10}")
    colors = {}
    for alpha_deg in alphas_deg:
        alpha_rad = np.radians(alpha_deg)
        s = s_of_phi(phi_rad, alpha_rad)
        line, = ax.plot(phi_deg, s, label=f"alpha = {alpha_deg} deg", linewidth=2)
        colors[alpha_deg] = line.get_color()
        # mirror across the upwind-downwind axis for the other tack
        axp.plot(phi_rad, s, color=line.get_color(), linewidth=2)
        axp.plot(-phi_rad, s, color=line.get_color(), linewidth=2)

        phi_max_deg, s_max = max_point(alpha_deg)
        ax.plot(phi_max_deg, s_max, marker="o", color=line.get_color(),
                 markersize=6, markeredgecolor="black", markeredgewidth=0.5)
        phi_max_rad = np.radians(phi_max_deg)
        for sign in (1, -1):
            axp.plot(sign * phi_max_rad, s_max, marker="o", color=line.get_color(),
                      markersize=6, markeredgecolor="black", markeredgewidth=0.5)
        print(f"{alpha_deg:>12} {phi_max_deg:>15.1f} {s_max:>10.2f}")

    print(f"\nWith {LEEWAY_DEG:.0f} deg of leeway (alpha_eff = alpha + {LEEWAY_DEG:.0f} deg):")
    print(f"{'alpha (deg)':>12} {'phi_max (deg)':>15} {'s_max':>10}")
    for alpha_deg in LEEWAY_ALPHAS_DEG:
        alpha_eff_deg = alpha_deg + LEEWAY_DEG
        alpha_eff_rad = np.radians(alpha_eff_deg)
        s = s_of_phi(phi_rad, alpha_eff_rad)
        ax.plot(phi_deg, s, label=f"alpha = {alpha_deg} deg + {LEEWAY_DEG:.0f} deg leeway",
                 linewidth=1.5, linestyle="--", color=colors[alpha_deg])
        axp.plot(phi_rad, s, color=colors[alpha_deg], linewidth=1.5, linestyle="--")
        axp.plot(-phi_rad, s, color=colors[alpha_deg], linewidth=1.5, linestyle="--")

        phi_max_deg, s_max = max_point(alpha_eff_deg)
        ax.plot(phi_max_deg, s_max, marker="o", color=colors[alpha_deg],
                 markersize=6, markerfacecolor="white", markeredgewidth=1.2)
        phi_max_rad = np.radians(phi_max_deg)
        for sign in (1, -1):
            axp.plot(sign * phi_max_rad, s_max, marker="o", color=colors[alpha_deg],
                      markersize=6, markerfacecolor="white", markeredgewidth=1.2)
        print(f"{alpha_deg:>12} {phi_max_deg:>15.1f} {s_max:>10.2f}")

    ax.set_xlabel("phi, course angle from upwind (degrees)")
    ax.set_ylabel("s / |w|  (windsurfer speed / wind speed)")
    ax.set_title("Kinematic windsurfer speed vs course angle")
    ax.set_xlim(0, 180)
    ax.set_ylim(bottom=0)
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend(fontsize=8)

    axp.set_title("Polar (sailing) diagram\nwind from the top (N), 0 deg = upwind")
    axp.grid(True, linewidth=0.5, alpha=0.5)

    fig.tight_layout()
    out_path = "windsurfer_speed.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to {out_path}")

    plt.show()


if __name__ == "__main__":
    main()
