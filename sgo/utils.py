class ColorPrint:
    COLORS = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
    }

    @staticmethod
    def print(text, color=None, end='\n'):
        if color:
            color_code = ColorPrint.COLORS.get(color.lower())
            print(f'\033[{color_code}m{text}\033[0m', end=end)
        else:
            print(text, end=end)

    @staticmethod
    def input(prompt, color=None):
        if color is not None:
            color_code = ColorPrint.COLORS.get(color.lower())
            print(f'\033[{color_code}m{prompt}\033[0m', end='')
        else:
            print(prompt, end='')
        try:
            user_input = input()
        except EOFError:
            print()
            return None
        return user_input
