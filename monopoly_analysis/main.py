import probabilities

if __name__ == "__main__":
    ini = probabilities.Probabilities()
    states = ini.create_state_space()
    matrix = ini.create_transition_matrix(states)
    print(len(matrix))
