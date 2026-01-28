import probabilities

if __name__ == "__main__":
    ini = probabilities.Probabilities()
    probs = ini.get_probabilities_of_community_chest_cards(16, 2)
    zustandsraum = ini.create_state_space()
    print(zustandsraum)
    print(len(zustandsraum))
