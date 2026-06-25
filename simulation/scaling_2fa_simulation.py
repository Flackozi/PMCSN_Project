import simulation.scaling_simulator as scal


def scaling_2fa_finite_simulation(stop):
    """
    Scaling simulation con 2FA: stessa logica di scaling_finite_simulation,
    ma con get_service_A e get_service_P patchati per i tempi 2FA
    (A3: 0.15 s, P: 0.7 s).
    """
    _orig_A = scal.get_service_A
    _orig_P = scal.get_service_P

    try:
        scal.get_service_A = scal.get_service_A_2FA
        scal.get_service_P = scal.get_service_P_2FA
        return scal.scaling_finite_simulation(stop)
    finally:
        scal.get_service_A = _orig_A
        scal.get_service_P = _orig_P
