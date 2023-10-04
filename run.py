import sys
import os
from dotenv import load_dotenv
load_dotenv()

# This is some code I reuse for any scripting projects I have.
# It's probably too complex for a project with only one command but it works...


def vix_controller(args):
    from vix.vix import Vix
    key = os.environ.get("TDAMER_KEY")
    ticker = args[0]

    vixvol = Vix(
        td_api_key=key,
        debug=False,
        caching_enabled=True
    )

    vix = vixvol.calculate(ticker)
    print('VIX: ' + str(vix))


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
