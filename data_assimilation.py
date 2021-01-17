import numpy as np
from adao import adaoBuilder
from operator import itemgetter


def assimilate(initial, yobs, observation_operator, evolution_func, error_vector=None, verbose=False,
               maximum_number_of_steps=100):
    xb = list(itemgetter('x', 'y', 'z', 'rho', 'sigma', 'beta')(initial))
    case = adaoBuilder.New('')
    case.setBackground(Vector=xb, Stored=True)
    if error_vector:
        case.setBackgroundError(DiagonalSparseMatrix=error_vector)
    else:
        case.setBackgroundError(ScalarSparseMatrix=1.e4)
    case.setEvolutionError(ScalarSparseMatrix=0.1)
    case.setEvolutionModel(OneFunction=evolution_func)
    case.setObservation(VectorSerie=yobs, Stored=True)
    case.setObservationError(ScalarSparseMatrix=0.1)
    case.setObservationOperator(OneFunction=observation_operator)
    case.setAlgorithmParameters(
        Algorithm='4DVAR',
        Parameters={
            'StoreSupplementaryCalculations': [
                # 'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum',
                # 'CostFunctionJb', 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo',
                # 'CostFunctionJoAtCurrentOptimum', 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
                'CurrentState'
            ],
            'MaximumNumberOfSteps': maximum_number_of_steps
        },
    )
    if verbose:
        calculations = [
            # 'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum', 'CostFunctionJb',
            # 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo', 'CostFunctionJoAtCurrentOptimum',
            # 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
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
