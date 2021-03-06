import numpy as np
from adao import adaoBuilder
from operator import itemgetter


def lorenz_obs_operator(state):
    x, y, z, rho, sigma, beta = state
    return [x, y, z]


def assimilate_lorenz(initial, observations, lorenz_step, error_vector=None, verbose=True,
                     maximum_number_of_steps=100):
    def lorenz_evol_step(state):
        list(np.ravel(state))
        x, y, z, rho, sigma, beta = state  # Unpack the state vector
        parameters = list(map(lambda param: abs(param), [rho, sigma, beta]))
        return np.array([lorenz_step([x, y, z], parameters), parameters]).reshape(-1, 1)

    background = list(itemgetter('x', 'y', 'z', 'rho', 'sigma', 'beta')(initial))
    case = adaoBuilder.New('')
    case.setBackground(Vector=background, Stored=True)
    if error_vector:
        case.setBackgroundError(DiagonalSparseMatrix=error_vector)
    else:
        case.setBackgroundError(ScalarSparseMatrix=1.e4)
    case.setEvolutionError(ScalarSparseMatrix=0.1)
    case.setEvolutionModel(OneFunction=lorenz_evol_step)
    case.setObservation(VectorSerie=observations, Stored=True)
    case.setObservationError(ScalarSparseMatrix=0.1)
    case.setObservationOperator(OneFunction=lorenz_obs_operator)
    case.setAlgorithmParameters(
        Algorithm='4DVAR',
        Parameters={
            'StoreSupplementaryCalculations': [
                'CurrentState'
            ],
            'MaximumNumberOfSteps': maximum_number_of_steps
        },
    )
    if verbose:
        calculations = [
            'CurrentState'
        ]
        for calculation in calculations:
            case.setObserver(
                Info="  Intermediate " + calculation + " at the current iteration:",
                Template='ValuePrinter',
                Variable=calculation,
            )
    case.execute()
    print("Calibration of %i coefficients on %i measures" % (
        len(case.get('Background')),
        len(case.get('Observation')),
    ))
    print("---------------------------------------------------------------------")
    print("Calibration resulting coefficients.:", np.ravel(case.get('Analysis')[-1]))
    x, y, z, rho, sigma, beta = np.ravel(case.get('Analysis')[-1])
    return dict(
        x=x,
        y=y,
        z=z,
        rho=rho,
        sigma=sigma,
        beta=beta
    )


def assimilate_lorenz_weighted(background, observations, observation_operator, verbose=True):
    case = adaoBuilder.New('')
    case.setBackground(Vector=background, Stored=True)
    # case.setBackgroundError(ScalarSparseMatrix=1.e6)
    case.setBackgroundError(ScalarSparseMatrix=1.e4)
    case.setObservation(Vector=observations, Stored=True)
    # case.setObservationError(ScalarSparseMatrix=1.)
    case.setObservationError(ScalarSparseMatrix=0.1)
    case.setObservationOperator(OneFunction=observation_operator)
    case.setAlgorithmParameters(
        Algorithm='3DVAR',
        Parameters={
            'StoreSupplementaryCalculations': [
                'CurrentState'
            ],
            'MaximumNumberOfSteps': 50
        },
    )
    if verbose:
        calculations = [
            'CurrentState'
        ]
        for calculation in calculations:
            case.setObserver(
                Info="  Intermediate " + calculation + " at the current iteration:",
                Template='ValuePrinter',
                Variable=calculation,
            )
    case.execute()
    print("Calibration of %i coefficients on %i measures" % (
        len(case.get('Background')),
        len(case.get('Observation')),
    ))
    print("---------------------------------------------------------------------")
    print("Calibration resulting coefficients.:", np.ravel(case.get('Analysis')[-1]))
    return np.ravel(case.get('Analysis')[-1])
