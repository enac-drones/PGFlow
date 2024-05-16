import argparse
from pgflow import Cases, run_simulation, SimulationVisualizer


def main():
    parser = argparse.ArgumentParser(description="Launch the SceneBuilder GUI")

    parser.add_argument(
        "-s",
        "--scene",
        type=str,
        help="Load a scene from a JSON file at the specified path.",
    )
    parser.add_argument(
        "-v",
        "--vis",
        action="store_true",
        help="Visualise the result of the simulation in matplotlib",
    )

    args = parser.parse_args()

    if not args.scene:
        raise ValueError("Please specify a scene to load.")

    file_name = args.scene

    print(f"Loading scene '{file_name}'...")
    case = Cases.get_case(file_name, case_name="default")

    print("Running simulation...")
    result = run_simulation(case, t=1500, update_every=1, stop_at_collision=False)
    case.to_dict(file_path="pgflow_output.json")

    if args.vis:
        print("Visualising the result of the simulation...")
        visualizer = SimulationVisualizer("pgflow_output.json")
        visualizer.show_plot()


if __name__ == "__main__":
    main()
