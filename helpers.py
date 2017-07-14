def check_empty(field):
    if field == "":
        return True
    else:
        return False

def check_length(field):
    if len(field) < 3 or len(field) > 20:
        return True
    else:
        return False

def check_space(field):
    for character in field:
        if character == " ":
            return True

    return False
