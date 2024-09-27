def normalize(name : str):
    name = name.strip().split()
    return " ".join(i.capitalize() for i in name)