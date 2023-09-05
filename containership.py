# TPK4186 - 2023 - Assignment 1

# 1. Imported modules
# -------------------

import datetime
import random
import math
import time

# 2. Containers
# -------------


def Container_New(serialNumber, length, weight, cargo):
    return [serialNumber, length, weight, cargo]


def Container_NewSmall(serialNumber, cargo):
    return Container_New(serialNumber, 20, 2, cargo)


def Container_NewBig(serialNumber, cargo):
    return Container_New(serialNumber, 40, 4, cargo)


def Container_GetSerialNumber(container):
    return container[0]


def Container_SetSerialNumber(container, serialNumber):
    container[0] = serialNumber


def Container_GetLength(container):
    return container[1]


def Container_SetLength(container, length):
    container[1] = length


def Container_GetWeight(container):
    if container is not None:
        # Check if container is a paired list with 20 feet containers
        if isinstance(container[0], list):
            return sum(sub_container[2] for sub_container in container)
        else:
            return container[2]
    else:
        return 0


def Container_SetWeight(container, weight):
    container[2] = weight


def Container_GetCargo(container):
    if container is not None:
        if isinstance(container[0], list):  # Check if container is paired
            return sum(sub_container[3] for sub_container in container)
        else:
            return container[3]
    else:
        return 0


def Container_SetCargo(container, cargo):
    container[3] = cargo


def Container_GetTotalWeight(container):
    total_weight = 0
    if container is not None:
        if isinstance(container[0], list):  # Check if container is paired
            for sub_container in container:
                total_weight += Container_GetWeight(
                    sub_container) + Container_GetCargo(sub_container)
        else:
            total_weight = Container_GetWeight(
                container) + Container_GetCargo(container)
    return total_weight


def Container_make_container_set(numberOfContainers):
    containers = []
    for _ in range(numberOfContainers):
        container = ContainerManager_NewRandomContainer()
        containers.append(container)
    return containers

# 3. Ships
# --------


def Ship_Stack():
    return [None for _ in range(18)]


def Ship_Section():
    return [Ship_Stack() for _ in range(11 * 4)]


def Ship_New(length, width, height):
    return [length, width, height,
            [Ship_Section() for _ in range(6)]]


def Ship_GetLength(ship):
    return ship[0]


def Ship_SetLength(ship, length):
    ship[0] = length


def Ship_GetWidth(ship):
    return ship[1]


def Ship_SetWidth(ship, width):
    ship[1] = width


def Ship_GetHeight(ship):
    return ship[2]


def Ship_SetHeight(ship, height):
    ship[2] = height


def Ship_GetAllContainers(ship):
    if ship is None:
        return [], 0
    containers = []
    count = 0
    for section in ship[3]:
        for stack in section:
            if stack is not None:
                for container in stack:
                    if container is not None:
                        containers.append(container)
                        count += 1
    return containers, count


def Ship_GetSection(ship, index):
    return ship[3][index]  # Retunerer hele seksjonen med containere


def Ship_GetNumberOfSections(ship):
    return len(ship[3])


def Ship_GetNumberOfContainers(ship):
    return len(Ship_GetAllContainers(ship))


def Ship_IsEmpty(ship):
    return Ship_GetNumberOfContainers(ship) == 0


def Ship_RemoveContainer(ship, container):
    container_id = Container_GetSerialNumber(container)
    for section in ship[3]:
        for stack in section:
            for i in range(len(stack)):
                current_container = stack[i]
                if current_container is not None and Container_GetSerialNumber(current_container) == container_id:
                    # Pop all containers above the removed container
                    popped_containers = Ship_PopContainers(
                        stack[i+1:], float('inf'))
                    stack = stack[:i]
                    # Insert the popped containers back into the stack, sorted by decreasing weight
                    for popped_container in popped_containers:
                        Ship_InsertContainer(stack, popped_container)
                    print(f"Container {container_id} has been removed.")
                    return
    print(f"Could not find container {container_id} on the ship.")


def Ship_FindContainer(ship, container):
    container_id = Container_GetSerialNumber(container)
    for section_idx, section in enumerate(ship[3]):
        for stack_idx, stack in enumerate(section):
            for i, current_container in enumerate(stack):
                if current_container is not None and Container_GetSerialNumber(current_container) == container_id:
                    return f"Container {container_id} found in section {section_idx+1}, stack {stack_idx+1}."
    return f"Container {container_id} was not found on the ship."


def Ship_GetLightestSection(ship):
    sections = ship[3]
    if not any(sections):
        # If all sections are empty, return the first section
        return sections[0]

    lightest_section = sections[0]
    lightest_total_weight = math.inf

    for section in sections:
        total_weight = 0
        for stack in section:
            for container in stack:
                if container is not None:
                    total_weight += Container_GetTotalWeight(container)
        if total_weight < lightest_total_weight:
            lightest_section = section
            lightest_total_weight = total_weight

    return lightest_section


def Ship_GetLightestStackInSection(section):
    lightest_weight = float('inf')
    lightest_stack = None
    for stack in section:
        current_weight = sum(Container_GetTotalWeight(c)
                             for c in stack if c is not None)
        if current_weight < lightest_weight:
            lightest_weight = current_weight
            lightest_stack = stack
    return lightest_stack


def Ship_GetLightestStackInSectionOrNext(section, container):
    lightest_stack = Ship_GetLightestStackInSection(section)
    if all(lightest_stack):
        lightest_stack = None
        lightest_weight = float('inf')
        for stack in section:
            if not all(stack):
                stack_weight = sum(Container_GetTotalWeight(c)
                                   for c in stack if c is not None)
                if stack_weight < lightest_weight:
                    lightest_stack = stack
                    lightest_weight = stack_weight
        if lightest_stack is None:
            # If all stacks in the section are full, find the next lightest section
            lightest_weight = float('inf')
            lightest_section = None
            for s in ship[3]:
                if not any(s):
                    lightest_section = s
                    break
                section_weight = sum(sum(Container_GetTotalWeight(c)
                                         for c in stack if c is not None) for stack in s)
                if section_weight < lightest_weight:
                    lightest_weight = section_weight
                    lightest_section = s
            lightest_stack = Ship_GetLightestStackInSection(lightest_section)
    return lightest_stack


def Ship_IsSectionFull(section):
    for stack in section:
        if not all(elem is not None for elem in stack):
            return False
    return True

# Core logic


def Ship_LoadContainer(ship, container):
    # Keeping track of operations
    operations = 0
    # Get the lightest section and stack
    lightest_section = Ship_GetLightestSection(ship)
    lightest_stack = Ship_GetLightestStackInSectionOrNext(
        lightest_section, container)

    # Pop all containers in the stack that are lighter than the new container
    popped_containers = Ship_PopContainers(
        lightest_stack, Container_GetTotalWeight(container))
    operations += len(popped_containers)
    # Insert the new container in the stack
    Ship_InsertContainer(lightest_stack, container)
    operations += 1

    # Insert the popped containers back into the stack, sorted by decreasing weight
    for popped_container in popped_containers:
        Ship_InsertContainer(lightest_stack, popped_container)
        operations += 1
    return operations


def Ship_load_container_from_containerset(ship, container_set):
    operations = 0
    new_container_set = Ship_PairContainers(container_set)
    for container in new_container_set:
        operations += Ship_LoadContainer(ship, container)
    return operations


def calculate_loading_time_with_one_crane(operations):
    total_min = operations * 4
    days = total_min // (60 * 24)
    hours = (total_min % (60 * 24)) // 60
    minutes = total_min % 60
    time_str = ""
    if days > 0:
        time_str += f"{days} days and "
    if hours > 0:
        time_str += f"{hours} hours and "
    time_str += f"{minutes} minutes"
    return time_str


def Ship_PairContainers(container_set):
    pairedContainers = []
    new_container_set = []
    for container in container_set:
        if Container_GetLength(container) == 20:
            if len(pairedContainers) == 1:
                pairedContainers.append(container)
                new_container_set.append(pairedContainers)
                pairedContainers = []
            else:
                pairedContainers.append(container)
        else:
            new_container_set.append(container)

    # If there's one small container left, add it to the end of the fixed container set
    if len(pairedContainers) == 1:
        new_container_set.append(pairedContainers[0])

    return new_container_set


def Ship_InsertContainer(stack, container):
    if container is None:
        raise ValueError("Invalid container: None")

    # If the container is a 2D list with two 20-foot containers, combine them into a single 40-foot container
    if isinstance(container, list) and len(container) == 2:
        container = [container[0], None, container[1], None]

    for i, cell in enumerate(stack):
        if cell is None:
            stack[i] = container
            return

    stack.append(container)


def Ship_UnloadContainers(ship):
    # keeping track over operations
    operations = 0
    removed_containers = []
    for i in range(Ship_GetNumberOfSections(ship)):
        section = Ship_GetSection(ship, i)
        for j in range(len(section)):
            stack = section[j]
            while len(stack) > 0:
                removed_containers.append(stack.pop())
                operations += 1
    return removed_containers, operations


def Ship_GetTotalWeightOfSection(section):
    total_weight = 0
    for stack in section:
        for container in stack:
            if container is not None:
                total_weight += Container_GetTotalWeight(container)
    return total_weight


def Ship_GetTotalWeight(ship):
    total_weight = 0
    for i in range(Ship_GetNumberOfSections(ship)):
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_GetTotalWeightOnStarboard(ship):
    total_weight = 0
    for i in range(3):  # Starboardsections is at index 0,1,2
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_GetTotalWeightOnPortSide(ship):
    total_weight = 0
    for i in range(3, 6):  # Portsidesections is at index 3,4,5
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_GetTotalWeightInFront(ship):
    total_weight = 0
    for i in range(0, 6, 3):  # Frontsection is at index 0 and 3
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_GetTotalWeightInMiddle(ship):
    total_weight = 0
    for i in range(1, 6, 3):  # Frontsection is at index 1 and 4
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_GetTotalWeightInBack(ship):
    total_weight = 0
    for i in range(2, 6, 3):  # Frontsection is at index 2 and 5
        total_weight += Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    return total_weight


def Ship_AllStacksAreInDecreasingOrder(ship):
    sections = ship[3]
    for i in range(len(sections)):
        section = sections[i]
        stack = section[i]
        if not Ship_IsStackInDecreasingOrder(stack):
            return False
    return True


def Ship_IsStackInDecreasingOrder(stack):
    for i in range(1, len(stack)):
        if stack[i] is not None and stack[i-1] is not None:
            if Container_GetTotalWeight(stack[i]) > Container_GetTotalWeight(stack[i-1]):
                return False
    return True


def Ship_StarboardAndPortsideWeightsAreBalanced(ship, max_percent_diff):
    total_weight = Ship_GetTotalWeight(ship)
    starboard_weight = Ship_GetTotalWeightOnStarboard(ship)
    portside_weight = Ship_GetTotalWeightOnPortSide(ship)

    percent_diff = abs(starboard_weight - portside_weight) / total_weight * 100
    if percent_diff <= max_percent_diff:
        return True
    else:
        return False


def Ship_SectionWeightsAreBalanced(ship, max_percent_difference):
    num_sections = Ship_GetNumberOfSections(ship)
    for i in range(num_sections):
        for j in range(i+1, num_sections):
            weight_i = Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
            weight_j = Ship_GetTotalWeightOfSection(Ship_GetSection(ship, j))
            percent_difference = abs(
                weight_i - weight_j) / max(weight_i, weight_j) * 100
            if percent_difference > max_percent_difference:
                return False
    return True


def Ship_CheckLoadBalance(ship, starboard_and_portside_percent=5, section_percent=10):
    if not Ship_AllStacksAreInDecreasingOrder(ship):
        print("The stacks are not in decreasing order.")

    if not Ship_SectionWeightsAreBalanced(ship, section_percent):
        print(
            f"The weight on a section of the ship exceeds the weight on another section by more than {section_percent}%.")

    if not Ship_StarboardAndPortsideWeightsAreBalanced(ship, starboard_and_portside_percent):
        print(
            f"The weight on starboard exceeds the weight on port side by more than {starboard_and_portside_percent}%.")
    if Ship_AllStacksAreInDecreasingOrder(ship) and Ship_SectionWeightsAreBalanced(ship, section_percent) and Ship_StarboardAndPortsideWeightsAreBalanced(ship, starboard_and_portside_percent):
        print("The load of the ship is balanced.")


def Ship_PopContainers(stack, threshold_weight):
    popped_containers = []
    i = 0
    while i < len(stack):
        container = stack[i]
        if container is not None and Container_GetTotalWeight(container) < threshold_weight:
            popped_containers.append(container)
            stack.pop(i)
        else:
            i += 1
    # Returning in decresing weight
    popped_containers.sort(key=Container_GetTotalWeight, reverse=True)
    return popped_containers


# 4: Printer
# ------------
def Containers_to_string(container_set):
    # Create header row for table
    header = "Serialnumber    | Length |  Weight | Cargo\n"
    separator = "-" * 16 + "|" + "-" * 8 + "|" + "-" * 9 + "|" + "-" * 12 + "\n"

    # Create rows for each container
    rows = []
    for container in container_set:
        serial_number = Container_GetSerialNumber(container)
        length = Container_GetLength(container)
        weight = Container_GetWeight(container)
        cargo = Container_GetCargo(container)

        # Format row as string and add to list
        row = f"{serial_number} | {length:>6} | {weight:>7} | {cargo}"
        rows.append(row)

    # Concatenate header, rows, and separator into final string
    return header + separator + "\n".join(rows)


def Ship_ToString(ship):
    str_list = []
    for i, section in enumerate(ship[3]):
        str_list.append(f"Section {i+1}:")
        for j in range(18):
            str_list.append(f"Floor {j+1}:")
            for k in range(4):
                stack_str = ""
                for l in range(11):
                    if (l * 4) + k < len(section) and j < len(section[(l * 4) + k]):
                        stack = section[(l * 4) + k][j]
                        if stack is None:
                            stack_str += " -"
                        else:
                            container_str = f"{'L' if stack[1] == 40 else 'S'}{Container_GetTotalWeight(stack)}"
                            # add the container to the start of the string
                            stack_str = f" {container_str}" + stack_str
                    else:
                        stack_str += " -"
                str_list.append(stack_str)
        str_list.append("")
    return "\n".join(str_list)


# 5. Container Manager
# --------------------
ContainerManager_number = 0


def ContainerManager_NewSerialNumber():
    global ContainerManager_number
    ContainerManager_number += 1
    today = datetime.datetime.today()
    date_string = today.strftime("%Y-%m-%d")
    return date_string + "-" + str(ContainerManager_number).zfill(4)


def ContainerManager_NewRandomContainer():
    serialNumber = ContainerManager_NewSerialNumber()
    isSmall = random.randint(0, 1)
    if isSmall == 0:
        cargo = random.randint(0, 20)
        container = Container_NewSmall(serialNumber, cargo)
    else:
        cargo = random.randint(0, 22)
        container = Container_NewBig(serialNumber, cargo)
    return container
# Write to file and load from file
# ---------------


def write_containers_to_file(containers, file_path):
    with open(file_path, "w") as file:
        for container in containers:
            serialnumber = Container_GetSerialNumber(container)
            length = Container_GetLength(container)
            weight_empty = Container_GetWeight(container)
            cargo = Container_GetCargo(container)
            file.write(f"{serialnumber} {length} {weight_empty} {cargo}\n")


def load_containers_from_file(file_path):
    containers = []
    with open(file_path, "r") as file:
        for line in file:
            container_data = line.strip().split(" ")
            serial_number = container_data[0]
            length = int(container_data[1])
            weight_empty = int(container_data[2])
            cargo = int(container_data[3])
            container = Container_New(
                serial_number, length, weight_empty, cargo)
            containers.append(container)
    return containers


# X. Main
# -------
ship = Ship_New(24, 22, 18)
container_set = Container_make_container_set(6500)
# print(Containers_to_string(container_set))

start = time.time()
operations = Ship_load_container_from_containerset(
    ship, container_set)  # Placing containers on ship
end = time.time()
# Ship_UnloadContainers(ship)

print(Ship_ToString(ship))

# running time on the code
print("It takes", end-start, "seconds to run this code")


write_containers_to_file(container_set, "container_set.tsv")
# print(load_containers_from_file("container_set.tsv"))


new_container = ContainerManager_NewRandomContainer()
Ship_LoadContainer(ship, new_container)
print(Ship_FindContainer(ship, new_container))
Ship_RemoveContainer(ship, new_container)


print("The total weight of the ship is: ", Ship_GetTotalWeight(ship))

for i in range(Ship_GetNumberOfSections(ship)):
    sectionWeight = Ship_GetTotalWeightOfSection(Ship_GetSection(ship, i))
    print("Section", i+1, "has weight: ", sectionWeight)

print("The total weight on startboard of the ship is: ",
      Ship_GetTotalWeightOnStarboard(ship))
print("The total weight on portside of the ship is: ",
      Ship_GetTotalWeightOnPortSide(ship))
print("\t")
print("The total weight in the front of the ship is: ",
      Ship_GetTotalWeightInFront(ship))
print("The total weight in the middle of the ship is: ",
      Ship_GetTotalWeightInMiddle(ship))
print("The total weight in the back of the ship is: ",
      Ship_GetTotalWeightInBack(ship))

Ship_CheckLoadBalance(ship, 5, 10)
print("\t")

print("Number of operations is: ", operations)
print("It takes ", calculate_loading_time_with_one_crane(
    operations), "to load the ship with one crane")
print("\t")
