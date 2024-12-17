import json
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import sys


TICK_FONTSIZE = 16
LABEL_FONTSIZE = 20
TITLE_FONTSIZE = 24


def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print("Need a file")
        return

    errors = []
    print(file_name)
    with open(file_name) as f:
        for line_str in f:
            line_lst = json.loads(line_str)
            errors.append(line_lst[2])
    print(np.mean(errors).round(3), end=' ')
    print(np.median(errors).round(3))

if __name__ == '__main__':
    main()
