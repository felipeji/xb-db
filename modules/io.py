from trm.molly import rmolly



def read_molly(file, index):
    wave = rmolly(file)[index].wave
    flux = rmolly(file)[index].f
    return wave, flux


def write_molly(molly_list,output):
    with open(output, 'wb') as fptr:
        for molly in molly_list:
            molly.write(fptr)


def select_molly(file_list, index_list):
    selected_list = []
    for file, index in zip(file_list, index_list):
        selected_list.append(rmolly(file)[index])
    return selected_list

    