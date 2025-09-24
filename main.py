from utils.docker_funcs import check_docker_setup, run_bash_command


def main():

    check_docker_setup()
    run_bash_command("date > date.txt")


if __name__ == "__main__":
    main()
