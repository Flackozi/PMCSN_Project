import utils.variables as vs

arrivalTemp = vs.START

def get_simulation(model):
    # print("Select model:")
    # print("1. Base model")
    # # print("2. Better")
    # # print("3. Standard Scalability")
    # # print("4. Better Scalability")
    # model = int(input("Select the number: "))

    # if model < 1 or model > 4:
    #     raise ValueError()

    # if model == 3 or model == 4:
    #     sim = 1
    # else:
    print("Select simulation:")
    print("1. Finite")
    print("2. Infinite")
    sim = int(input("Select the number: "))

    if sim < 1 or sim > 2:
        raise ValueError()

    
    vs.set_simulation(model, sim)


def reset_arrival_temp():
    global arrivalTemp
    arrivalTemp = vs.START