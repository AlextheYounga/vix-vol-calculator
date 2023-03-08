import sys
import colored
from colored import stylize
from dotenv import load_dotenv
load_dotenv()

# This is some code I reuse for any scripting projects I have.
# It's probably too complex for a project with only one command but it works.

def vix_controller(args):
    from vix.vix import run_vix_equation

    ticker = args[0]
    print('VIX: '+str(run_vix_equation(ticker)))


def main():
    sys.argv.pop(0)

    args = [arg.strip() for arg in sys.argv]

    if (':' in args[0]):
        command = args.pop(0)
        program = command.split(':')[0] + "_controller"
        subroutine = command.split(':')[1]

        globals()[program](subroutine, args)
        return
    else:
        program = args.pop(0) + "_controller"

        globals()[program](args)
        return


if __name__ == '__main__':
    main()
