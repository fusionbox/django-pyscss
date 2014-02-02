

def clean_css(string):
    # The output of the compiled CSS doesn't have a newline between the ; and
    # the } for some reason.
    return string.strip() \
        .replace('\n', '') \
        .replace('; ', ';')
