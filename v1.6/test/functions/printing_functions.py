#=======================================================================================================================
#========================================= P R I N T I N G  F U N C T I O N S =========================================
#=======================================================================================================================

def get_color(name):
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
    return locals().get(name, RESET)

def print_console(color,text,width=120,character="=",space=True,top=False,break_line=True):
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

