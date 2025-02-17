import platform

def get_port():
    if 'Microsoft' in platform.uname().release:  # "Linux" under WSL
        if platform.node() == "SBK": return 5002
        if platform.node() == "SAG": return 5004
    elif platform.system() == "Windows":  # running under "Windows"
        if platform.node() == "SBK": return 5001
        if platform.node() == "SAG": return 5003
    return 5001  # default port

if __name__ == "__main__":
    print(get_port())
