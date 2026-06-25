import simulation.realistic_simulator as realistic


def realistic_2fa_finite_simulation(stop):
    """
    Simulazione realistica con 2FA: stessi arrivi del modello realistico
    (lambda variabile + iper-esponenziale), con tempi di servizio 2FA.
    """
    original_A = realistic.get_service_A
    original_P = realistic.get_service_P

    try:
        realistic.get_service_A = realistic.get_service_A_2FA
        realistic.get_service_P = realistic.get_service_P_2FA
        return realistic.realistic_finite_simulation(stop)
    finally:
        realistic.get_service_A = original_A
        realistic.get_service_P = original_P
