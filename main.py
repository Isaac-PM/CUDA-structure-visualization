import vtk
from rich.console import Console
from rich.table import Table

SPACING = 0.75
RED_COLOR = (1, 0, 0)
GREEN_COLOR = (0, 1, 0)
BLUE_COLOR = (0, 0, 1)
WHITE_COLOR = (1, 1, 1)


def create_cube(renderer, center, width, height, depth, color):
    cubeSource = vtk.vtkCubeSource()
    cubeSource.SetBounds(
        center[0] - width / 2.0,
        center[0] + width / 2.0,
        center[1] - height / 2.0,
        center[1] + height / 2.0,
        center[2] - depth / 2.0,
        center[2] + depth / 2.0,
    )

    cubeMapper = vtk.vtkPolyDataMapper()
    cubeMapper.SetInputConnection(cubeSource.GetOutputPort())

    cubeActor = vtk.vtkActor()
    cubeActor.SetMapper(cubeMapper)
    cubeActor.GetProperty().SetColor(color)
    renderer.AddActor(cubeActor)


# ------------------------------------------------
# --- Renderer

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# ------------------------------------------------
# --- User input

console = Console()

console.print("Instructions:", style="bold underline")
instructions = [
    "The 'dimension of the grid' refers to the layout of blocks within the grid, defined as a 2D matrix.",
    "Each block within this grid is further divided into a 3D matrix, called 'dimension of the block'.",
    "Note: The z-dimension of the grid is always set to 1 because it is a 2D matrix.",
]
for index, instruction in enumerate(instructions, start=1):
    console.print(f"[bold]{index}.[/bold] {instruction}")

option = 0

dim_grid = None
dim_block = None

console.print(
    "Write [bold]1[/bold] to display pre-defined values or [bold]2[/bold] to enter custom values."
)
option = int(console.input("Enter your choice: "))

if option == 1:
    table = Table(title="Pre-defined Choices")
    table.add_column("Choice Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Grid Dimensions", style="magenta")
    table.add_column("Block Dimensions", style="green")

    table.add_row("1", "2x2 grid", "4x2x2 blocks")
    table.add_row("2", "3x3 grid", "5x5x4 blocks")
    table.add_row("3", "1x1 grid", "8x8x8 blocks")

    console.print(table)

    choice = int(console.input("Enter your choice: "))
    if choice == 1:
        dim_grid = "2,2,1"
        dim_block = "4,2,2"
    elif choice == 2:
        dim_grid = "3,3,1"
        dim_block = "5,5,4"
    elif choice == 3:
        dim_grid = "1,1,1"
        dim_block = "8,8,8"
elif option == 2:
    dim_grid = console.input(
        "Enter the dimensions of the grid as three numbers separated by commas (x, y, and z, where z should be 1), e.g., 2,2,1: "
    )
    dim_block = console.input(
        "Enter the dimensions of the block as three numbers separated by commas (x, y, and z), e.g., 4,2,2: "
    )

dim_grid = [int(x) for x in dim_grid.split(",")]
dim_block = [int(x) for x in dim_block.split(",")]


# ------------------------------------------------
# --- Counts and dimensions

general_length = 0.5

thread_x_count = dim_block[0]
thread_y_count = dim_block[2]
thread_z_count = dim_block[1]
thread_x_length = general_length
thread_y_length = general_length
thread_z_length = general_length

block_x_count = dim_grid[0]
block_y_count = 1
block_z_count = dim_grid[1]
block_x_length = thread_x_count * (thread_x_length + SPACING)
block_y_length = 0.5
block_z_length = thread_z_count * (thread_z_length + SPACING)

console.print()
console.print(
    f"Total number of threads: {thread_x_count * thread_y_count * thread_z_count * block_x_count * block_y_count * block_z_count}",
    style="bold red",
)
console.print(
    f"Total number of blocks: {block_x_count * block_y_count * block_z_count}",
    style="bold blue",
)
console.print(
    f"Total number of threads in a block: {thread_x_count * thread_y_count * thread_z_count}",
    style="bold green",
)

# ------------------------------------------------
# --- Generate threads

first_and_last_thread_positions = []

for block_x in range(block_x_count):
    for block_y in range(block_y_count):
        for block_z in range(block_z_count):
            for thread_x in range(thread_x_count):
                for thread_y in range(thread_y_count):
                    for thread_z in range(thread_z_count):

                        thread = vtk.vtkCubeSource()
                        thread.SetXLength(thread_x_length)
                        thread.SetYLength(thread_y_length)
                        thread.SetZLength(thread_z_length)

                        thread_mapper = vtk.vtkPolyDataMapper()
                        thread_mapper.SetInputConnection(thread.GetOutputPort())

                        thread_actor = vtk.vtkActor()
                        thread_actor.SetMapper(thread_mapper)

                        thread_x_position = block_x * (
                            block_x_length + SPACING
                        ) + thread_x * (thread_x_length + SPACING)
                        thread_y_position = (block_y + 1) * (
                            block_y_length + SPACING
                        ) + thread_y * (thread_y_length + SPACING)
                        thread_z_position = block_z * (
                            block_z_length + SPACING
                        ) + thread_z * (thread_z_length + SPACING)

                        if (thread_x == 0 and thread_y == 0 and thread_z == 0) or (
                            thread_x == thread_x_count - 1
                            and thread_y == 0
                            and thread_z == thread_z_count - 1
                        ):
                            first_and_last_thread_positions.append(
                                (
                                    thread_x_position,
                                    thread_y_position,
                                    thread_z_position,
                                )
                            )

                        thread_actor.SetPosition(
                            thread_x_position, thread_y_position, thread_z_position
                        )
                        thread_actor.GetProperty().SetColor(RED_COLOR)
                        renderer.AddActor(thread_actor)

# ------------------------------------------------
# --- Generate blocks

first_and_last_thread_positions_joined = []

for i in range(0, len(first_and_last_thread_positions) - 1, 2):
    joined = []
    joined.append(first_and_last_thread_positions[i])
    joined.append(first_and_last_thread_positions[i + 1])
    first_and_last_thread_positions_joined.append(joined)

for position in first_and_last_thread_positions_joined:
    x1, y1, z1 = position[0]
    x2, y2, z2 = position[1]

    center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0)
    center = (center[0], center[1] - SPACING, center[2])

    width = abs(x2 - x1)
    height = 0.5
    depth = abs(z2 - z1)

    create_cube(renderer, center, width, height, depth, GREEN_COLOR)

# ------------------------------------------------
# --- Generate grid

first_position = first_and_last_thread_positions_joined[0]
last_position = first_and_last_thread_positions_joined[-1]

x1, y1, z1 = first_position[0]
x2, y2, z2 = last_position[1]

center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0)
center = (center[0], center[1] - SPACING * 2, center[2])

width = abs(x2 - x1)
height = 0.5
depth = abs(z2 - z1)

create_cube(renderer, center, width, height, depth, BLUE_COLOR)

# ------------------------------------------------
# --- Visualize

renderer.SetBackground(WHITE_COLOR)
renderWindow.Render()
renderWindow.SetSize(800, 800)
renderWindow.SetWindowName("3D Visualization of CUDA Thread Blocks")
renderWindowInteractor.Start()
