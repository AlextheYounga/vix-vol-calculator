import sys
import colored
from colored import stylize
from vix.output import printTabs
from dotenv import load_dotenv
load_dotenv()


def list_commands():
    headers = ['Command', 'Description']
    print("\n")
    print('Available Subcommands')
    print('No quotes required on [<ticker>] arguments, may be typed directly into the terminal.')
    print("\n\n")

    commands = [
        ['vix [<ticker>] [--debug]', 'Runs the VIX volatility equation on a ticker'],
    ]

    printTabs(commands, headers, 'simple')
    print("\n\n")


def command_error(required={}, opt=None):
    if(not (required or opt)):
        print(stylize("Error: your command did not match any known programs. Closing...", colored.fg("red")))
        print("\n")
        return

    if (required):
        print(stylize("FAILED: Requires arguments: ", colored.fg("red")))
        for typ, var in required.items():
            print(stylize("({}) [{}]".format(typ, var), colored.fg("red")))
        print("\n")
    if (opt):
        print(stylize("Optional arguments: ", colored.fg("yellow")))
        if (isinstance(opt, dict)):
            for typ, var in opt.items():
                print(stylize("({}) [{}]".format(typ, var), colored.fg("yellow")))
        if (isinstance(opt, list)):
            for var in opt.items():
                print(stylize("[{}]".format(var), colored.fg("yellow")))
            print("\n")


def vix_controller(args):
    required = {"string": "ticker"}
    opt = {"string": "--debug"}

    if (not args):
        command_error(required, opt)
        return

    from vix.equation import vix_equation

    ticker = args[0]
    print('VIX: '+str(vix_equation(ticker)))


def main():
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab.settings')
    sys.argv.pop(0)

    args = [arg.strip() for arg in sys.argv]


    if (args[0] == 'list'):
        list_commands()
        return

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

    print(stylize("Error: your command did not match any known programs. Closing...", colored.fg("red")))
    sys.exit()


if __name__ == '__main__':
    main()
