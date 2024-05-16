# import matplotlib.pyplot as plt
# import ipywidgets as widgets
# from IPython.display import display

class PIDController:
    def __init__(self, Kp, Ki, Kd, min_output, max_output):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.min_output = min_output
        self.max_output = max_output
        self.cumulative_error = 0
        self.previous_error = 0

    def update(self, error, dt):
    
        # Proportional term
        P = self.Kp * error

        # Integral term
        self.cumulative_error += error * dt
        I = self.Ki * self.cumulative_error

        # Derivative term
        error_rate = (error - self.previous_error) / dt
        D = self.Kd * error_rate

        # Compute the control signal
        control = P + I + D

        # Clamp the output
        control = max(self.min_output, min(control, self.max_output))

        # Update previous error
        self.previous_error = error

        return control
    
    def adjust_acceleration(self, v, a, max_v, min_v, dt):
        # Predict the next velocity
        predicted_v = v + a * dt

        # Adjust acceleration if the predicted velocity exceeds limits
        if predicted_v > max_v:
            a = (max_v - v) / dt
        elif predicted_v < min_v:
            a = (min_v - v) / dt

        return a

class VehicleDynamics:
    def __init__(self, mass, min_accel, max_accel):
        self.mass = mass
        self.min_accel = min_accel
        self.max_accel = max_accel
        # Initialize other parameters specific to the vehicle dynamics
    
    def update_state_verlet(self, x, vx, y, vy, ax, ay, dt):
        # Update position using Velocity Verlet
        x_new = x + vx * dt + 0.5 * ax * dt**2
        y_new = y + vy * dt + 0.5 * ay * dt**2

        # Predict the next velocity (half step)
        vx_half = vx + 0.5 * ax * dt
        vy_half = vy + 0.5 * ay * dt

        # Update acceleration here based on new position if needed
        # For constant acceleration, this step can be skipped

        # Complete the velocity update (second half step)
        vx_new = vx_half + 0.5 * ax * dt
        vy_new = vy_half + 0.5 * ay * dt

        return x_new, vx_new, y_new, vy_new



def adjust_acceleration(v, a, max_v, min_v, dt):
    # Predict the next velocity
    predicted_v = v + a * dt

    # Adjust acceleration if the predicted velocity exceeds limits
    if predicted_v > max_v:
        a = (max_v - v) / dt
    elif predicted_v < min_v:
        a = (min_v - v) / dt

    return a


if __name__ == "__main__":
    # Simulation parameters
    dt = 0.01
    simulation_time = 30
    min_accel, max_accel = -2.0, 2.0
    x_desired, y_desired = 1, 1
    Kp, Ki, Kd = 32, 0.05, 8.4

    vehicle = VehicleDynamics(mass=1, min_accel = -2, max_accel = 2)

    pid_x = PIDController(Kp, Ki, Kd, vehicle.min_accel, vehicle.max_accel)
    pid_y = PIDController(Kp, Ki, Kd, vehicle.min_accel, vehicle.max_accel)

    x, vx, y, vy = 0, -1, 0, -1
    all_x, all_y = [x], [y]
    acc_x, acc_y = [0], [0]
    v_x, v_y = [vx], [vy]
    times = [0]

    min_velocity, max_velocity = -1,1
    for t in range(int(simulation_time / dt)):
        error_x = x_desired - x
        error_y = y_desired - y

        ax = pid_x.update(error_x, dt)
        ay = pid_y.update(error_y, dt)

        # Adjust acceleration based on current velocity and limits
        ax = adjust_acceleration(vx, ax, max_velocity, min_velocity, dt)
        ay = adjust_acceleration(vy, ay, max_velocity, min_velocity, dt)

        # x, vx, y, vy = update_drone_state(x, vx, y, vy, ax, ay, dt)
        x, vx, y, vy = vehicle.update_state_verlet(x, vx, y, vy, ax, ay, dt)

        all_x.append(x)
        all_y.append(y)
        acc_x.append(ax)
        acc_y.append(ay)
        v_x.append(vx)
        v_y.append(vy)
        times.append(t * dt)

    

