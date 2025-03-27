from utils.monitoring import get_top_processes, RESOURCE_TYPE


if __name__ == "__main__":
    result = get_top_processes(5, sort_by=RESOURCE_TYPE.CPU)

    for p in result:
        print(p)
