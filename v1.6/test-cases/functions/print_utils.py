#=======================================================================================================================
"""
This file contains functions for printing colored text to the console.
It includes a function to get a color based on a name and a function to print formatted text with optional styling.
"""
#=======================================================================================================================


#=======================================================================================================================
#========================================= P R I N T I N G  F U N C T I O N S =========================================
#=======================================================================================================================

def get_color(name):
    """
    Returns the ANSI escape code for a given color name.
    :param name: Name of the color (case-insensitive).
    :return: ANSI escape code for the color, or RESET if the name is not recognized.
    """
    name = name.upper()
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    GREY = "\033[90m"
    # Additional colors
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    BLACK = "\033[30m"
    ORANGE = "\033[38;5;208m"   # 256-color mode
    PURPLE = "\033[35m"
    BROWN = "\033[38;5;94m"     # Approximation
    PINK = "\033[38;5;200m"     # Approximation
    LIGHT_GREEN = "\033[38;5;120m"
    LIGHT_BLUE = "\033[38;5;117m"
    PALE_PINK = "\033[38;5;217m"
    PALE_BLUE = "\033[38;5;153m"
    PALE_GREEN = "\033[38;2;178;237;192m"  # RGB for a pale green
    PALE_RED = "\033[38;5;167m"
    return locals().get(name, RESET)

def print_console(color,text,width=120,character="=",space=True,top=False,break_line=False):
    """
    Prints formatted text to the console with optional color, width, and character styling.
    :param color: Color name for the text (case-insensitive).
    :param text: Text to print.
    :param width: Width of the printed line (default is 120).
    :param character: Character to use for the top and bottom borders (default is "=").
    :param space: If True, adds spaces between words (default is True).
    :param top: If True, only prints the top border (default is False).
    :param break_line: If True, adds a newline after printing (default is False).
    """
    
    if break_line:
        print("\n")
    if space:
        text = " ".join(text)
    text = text.upper()
    if character == " " or character == "":
        print(f"{get_color(color)}{text.center(width)}{get_color('RESET')}")    
    else:
        if character == "=" or top:
            print(f"{get_color(color)}{character*width}{get_color('RESET')}")
        print(f"{get_color(color)}{text.center(width)}{get_color('RESET')}")
        print(f"{get_color(color)}{character*width}{get_color('RESET')}")

