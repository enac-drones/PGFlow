import numpy as np
from numpy.typing import ArrayLike
from scipy.integrate import solve_ivp
from typing import Optional
from numpy.typing import ArrayLike


def dynamics_matrices(dt: float) -> tuple[ArrayLike]:
    """Define matrices A and B based on dt
    to use:
    Define your current state X and control input U
    X = np.array([PE, PN, PU, Vx, Vy, Vz])  # Example values for current state
    U = np.array([VdesE, VdesN, VdesU])  # Control inputs based on desired direction
    X_next = A @ X + B @ U
    """
    k = 1.140  # Constant from your dynamics
    A = np.array(
        [
            [1.0, 0.0, 0.0, dt, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, dt, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, dt],
            [0.0, 0.0, 0.0, 1.0 - k * dt, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0 - k * dt, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0 - k * dt],
        ]
    )
    B = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [k * dt, 0.0, 0.0],
            [0.0, k * dt, 0.0],
            [0.0, 0.0, k * dt],
        ]
    )
    return A, B


def dynamics(t, X, U):
    # Assuming U is constant over the integration period
    # Define A and B inside the function or use global variables
    A, B = dynamics_matrices(t)
    Xdot = A @ X + B @ U - X
    return Xdot


def get_next_X(
    X0: ArrayLike, U: ArrayLike, delta_t: float, num_points: Optional[int] = 20
):
    # Your current state X and a desired direction vector turned into U
    # X0 = np.array([PE, PN, PU, Vx, Vy, Vz])  # Current state
    # U = np.array([VdesE, VdesN, VdesU])  # Desired velocities based on APF

    # Time bounds for integration, say you want to predict the next state in 1 second
    t_span = (0, delta_t)  # From 0 to delta_t seconds
    t_eval = np.linspace(
        *t_span, num_points
    )  # Evaluate the solution at 100 points within the interval

    # Solve the ODE
    sol = solve_ivp(
        fun=dynamics, t_span=t_span, y0=X0, args=(U,), t_eval=t_eval, method="RK45"
    )

    # sol.y will contain the integrated state over time
    # The final column in sol.y will give you the next position and velocity
    next_X = sol.y[:, -1]

    return next_X
