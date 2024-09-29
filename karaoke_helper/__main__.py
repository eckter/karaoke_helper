from .ui.runner import Runner


def entrypoint():
    runner = Runner()
    runner.run()


if __name__ == "__main__":
    entrypoint()