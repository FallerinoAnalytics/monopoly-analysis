import probabilities

if __name__ == "__main__":
    ini = probabilities.Probabilities()
    probs = ini.get_probabilities_of_community_chest_cards(16, 2)
    ini.get_states_after_frist_roll(probabilities.MonopolyState(0, 0, False), ini.dice_probabilities, ini.doubles_probabilities)
