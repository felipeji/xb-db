from trm.molly import rmolly



def read_molly(file, index):
    wave = rmolly(file)[index].wave
    flux = rmolly(file)[index].f
    return wave, flux


def wmolly(molly_list,output):
    with open(output, 'wb') as fptr:
        for molly in molly_list:
            molly.write(fptr)




    