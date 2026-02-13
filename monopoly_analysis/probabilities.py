from dataclasses import dataclass
from collections import Counter, defaultdict
import numpy as np
import game_board


@dataclass(frozen=True)
class MonopolyState:
    position: int  # Field Number
    counter: int  # Doubles Counter / Round in Jail Counter
    in_jail: bool  # True only on Field 10 possible

    def __hash__(self):
        return hash((self.position, self.counter, self.in_jail))


class Probabilities:
    def __init__(self):
        self.game_version = game_board.GermanMonopoly()
        self.doubles_probabilities = self.get_doubles_probabilities()
        self.non_doubles_probabilities = self.get_dice_probabilities(True)
        self.board_fields = self.game_version.board_fields
        self.jail_field = self.game_version.jail_field  # 10 (int)
        self.go_in_jail_field = self.game_version.go_in_jail_field  # 30 (int)

    @staticmethod
    def get_dice_probabilities(exclude_doubles: bool = False) -> dict[int, float]:
        if exclude_doubles:
            sums = (
                d1 + d2
                for d1 in range(1, 7)
                for d2 in range(1, 7)
                if d1 != d2
            )
        else:
            sums = (
                d1 + d2
                for d1 in range(1, 7)
                for d2 in range(1, 7)
            )

        sum_counts = Counter(sums)
        total_outcomes = 36

        return {
            dice_sum: round(sum_counts.get(dice_sum, 0) / total_outcomes, 4)
            for dice_sum in range(2, 13)
        }

    @staticmethod
    def get_doubles_probabilities() -> dict[int, float]:
        sums = (
            d1 + d2
            for d1 in range(1, 7)
            for d2 in range(1, 7)
            if d1 == d2
        )

        sum_counts = Counter(sums)
        total_outcomes = 36

        return {
            dice_sum: round(count / total_outcomes, 4)
            for dice_sum, count in sum_counts.items()
        }

    def create_state_space(self) -> list[MonopolyState]:
        states = []
        for pos in self.board_fields:
            if pos == self.go_in_jail_field:  # it's not possible to end a move on "go in jail"-field!
                continue
            for counter in range(3):
                states.append(MonopolyState(pos, counter, False))  # counter = doubles streak
                if pos == self.jail_field:
                    states.append(MonopolyState(pos, counter, True))  # counter = rounds in jail

        return states

    @staticmethod
    def _calculate_target_field(current_pos: int, dice_sum: int) -> int:
        """
            Berechnet das Zielfeld nach einem Würfelwurf.

            Args:
                current_pos: Aktuelles Feld (0-39)
                dice_sum: Würfelsumme (2-12)

            Returns:
                Zielfeld (0-39), berücksichtigt Überlauf über Los
            """
        return (current_pos + dice_sum) % 40

    def _get_chance_targets(self, current_pos: int) -> dict[int, float]:
        """
            Berechnet die Zielfelder und Wahrscheinlichkeiten für Ereigniskarten.

            Args:
                source_field: Das Ereignisfeld (7, 22 oder 36)

            Returns:
                Dictionary {Zielfeld: Wahrscheinlichkeit}

            Note:
                Feld 10 bedeutet hier "Gefängnis eingesperrt", nicht "Nur zu Besuch".
                Diese Unterscheidung wird in _create_target_state behandelt.
                :param current_pos:
            """
        total_cards = self.game_version.total_cards
        pos_changing = self.game_version.position_changing_chance_cards
        prob_per_card = 1 / total_cards
        prob_no_change = (total_cards - pos_changing) / total_cards

        # Feste Ziele (unabhängig vom Quellfeld)
        targets = {}
        for field in self.game_version.chance_card_fixed_targets:
            targets[field] = targets.get(field, 0) + prob_per_card

        # Feldabhängiges Ziel: Nächster Bahnhof
        next_railroad = self.game_version.get_next_railroad(current_pos)
        targets[next_railroad] = targets.get(next_railroad, 0) + prob_per_card

        # Feldabhängiges Ziel: 3 Felder zurück
        three_back = self.game_version.get_three_back(current_pos)
        targets[three_back] = targets.get(three_back, 0) + prob_per_card

        # Keine Positionsänderung (bleibt auf dem Ereignisfeld)
        targets[current_pos] = targets.get(current_pos, 0) + prob_no_change

        return targets

    def _get_community_targets(self, current_pos: int) -> dict[int, float]:
        """
            Berechnet die Zielfelder und Wahrscheinlichkeiten für Gemeinschaftskarten.

            Args:
                source_field: Das Gemeinschaftsfeld (2, 17 oder 33)

            Returns:
                Dictionary {Zielfeld: Wahrscheinlichkeit}

            Note:
                Feld 10 bedeutet hier "Gefängnis eingesperrt", nicht "Nur zu Besuch".
                Diese Unterscheidung wird in _create_target_state behandelt.
                :param current_pos:
            """
        total_cards = self.game_version.total_cards
        pos_changing = self.game_version.position_changing_community_cards
        prob_per_card = 1 / total_cards
        prob_no_change = (total_cards - pos_changing) / total_cards

        # Feste Ziele
        targets = {}
        for field in self.game_version.community_chest_fixed_targets:
            targets[field] = targets.get(field, 0) + prob_per_card

        # Keine Positionsänderung (bleibt auf dem Gemeinschaftsfeld)
        targets[current_pos] = targets.get(current_pos, 0) + prob_no_change

        return targets

    def _create_target_state(self,
                             target_field: int,
                             current_doubles: int,
                             is_double: bool,
                             from_jail_card: bool = False) -> MonopolyState:
        """
            Erstellt den korrekten Zielzustand basierend auf Zielfeld und Pasch-Status.

            Args:
                target_field: Das Zielfeld (0-39)
                current_doubles: Aktueller Pasch-Zähler (0, 1 oder 2)
                is_double: Wurde ein Pasch gewürfelt?
                from_jail_card: Wurde das Zielfeld durch eine Karte erreicht?

            Returns:
                MonopolyState: Der korrekte Zielzustand
            """
        # Fall 1: Feld 30 führt immer ins Gefängnis
        if target_field == self.go_in_jail_field:
            return MonopolyState(self.jail_field, 0, True)
        # Fall 2: Feld 10 durch Karte = Gefängnis (eingesperrt)
        if target_field == self.jail_field and from_jail_card:
            return MonopolyState(self.jail_field, 0, True)
        # Fall 3: Dritter Pasch führt ins Gefängnis
        if current_doubles == 2 and is_double:
            return MonopolyState(self.jail_field, 0, True)
        # Fall 4: Normaler Übergang
        if is_double:
            new_doubles = current_doubles + 1
        else:
            new_doubles = 0

        return MonopolyState(target_field, new_doubles, False)

    def _get_transitions_from_normal_state(self, state: MonopolyState) -> dict[MonopolyState, float]:
        """
            Berechnet alle möglichen Übergänge von einem freien Zustand.

            Args:
                state: Ausgangszustand (muss in_jail=False haben)

            Returns:
                Dictionary {Zielzustand: Wahrscheinlichkeit}
            """
        transitions = {}
        current_pos = state.position
        current_doubles = state.counter

        # Alle Würfelsummen durchgehen
        for dice_sum in range(2, 13):
            # Fall A: Kein Pasch
            prob_no_double = self.non_doubles_probabilities.get(dice_sum, 0)
            if prob_no_double > 0:
                self._add_transition(
                    transitions=transitions,
                    current_pos=current_pos,
                    dice_sum=dice_sum,
                    current_doubles=current_doubles,
                    is_double=False,
                    probability=prob_no_double
                )
            # Fall B: Pasch
            prob_double = self.doubles_probabilities.get(dice_sum, 0)
            if prob_double > 0:
                self._add_transition(
                    transitions=transitions,
                    current_pos=current_pos,
                    dice_sum=dice_sum,
                    current_doubles=current_doubles,
                    is_double=True,
                    probability=prob_double
                )

        return transitions

    def _add_transition(self,
                        transitions: dict[MonopolyState, float],
                        current_pos: int,
                        dice_sum: int,
                        current_doubles: int,
                        is_double: bool,
                        probability: float
                        ) -> None:
        """
            Fügt Übergang(e) für einen einzelnen Wurf zum transitions-Dictionary hinzu.

            Args:
                transitions: Dictionary, das modifiziert wird
                current_pos: Aktuelle Position
                dice_sum: Würfelsumme
                current_doubles: Aktueller Pasch-Zähler
                is_double: Ist es ein Pasch?
                probability: Wahrscheinlichkeit dieses Wurfs
            """
        # Dritter Pasch → direkt ins Gefängnis (Zielfeld irrelevant)
        if current_doubles == 2 and is_double:
            target_state = MonopolyState(self.jail_field, 0, True)
            transitions[target_state] = transitions.get(target_state, 0) + probability
            return

        # Zielfeld berechnen
        target_field = self._calculate_target_field(current_pos, dice_sum)

        # Feld 30 → Gefängnis
        if target_field == self.go_in_jail_field:
            target_state = MonopolyState(self.jail_field, 0, True)
            transitions[target_state] = transitions.get(target_state, 0) + probability
            return

        # Ereignisfeld
        if target_field in self.game_version.chance_fields:
            self._add_chance_card_transitions(
                transitions=transitions,
                current_pos=target_field,
                current_doubles=current_doubles,
                is_double=is_double,
                probability=probability
            )
            return

        # Gemeinschaftsfeld
        if target_field in self.game_version.community_fields:
            self._add_community_transitions(
                transitions=transitions,
                current_pos=target_field,
                current_doubles=current_doubles,
                is_double=is_double,
                probability=probability
            )
            return

        # Normales Feld
        target_state = self._create_target_state(
            target_field=target_field,
            current_doubles=current_doubles,
            is_double=is_double,
            from_jail_card=False
        )
        transitions[target_state] = transitions.get(target_state, 0) + probability

    def _add_chance_card_transitions(self,
                                     transitions: dict[MonopolyState, float],
                                     current_pos: int,
                                     current_doubles: int,
                                     is_double: bool,
                                     probability: float
                                     ) -> None:
        """
            Fügt alle möglichen Übergänge nach dem Ziehen einer Ereigniskarte hinzu.

            Args:
                transitions: Dictionary, das modifiziert wird
                current_pos: Das Ereignisfeld (7, 22 oder 36)
                current_doubles: Aktueller Pasch-Zähler
                is_double: Wurde ein Pasch gewürfelt?
                probability: Wahrscheinlichkeit, auf diesem Feld zu landen
            """
        card_targets = self._get_chance_targets(current_pos)

        for target_field, card_prob in card_targets.items():
            combined_prob = probability * card_prob

            # Prüfen ob "Gehe ins Gefängnis"-Karte
            is_jail_card = (target_field == self.jail_field)

            # Sonderfall: Zielfeld ist Gemeinschaftsfeld (Feld 36 → 3 zurück → Feld 33)
            if target_field in self.game_version.community_fields:
                self._add_community_transitions(
                    transitions=transitions,
                    current_pos=target_field,
                    current_doubles=current_doubles,
                    is_double=is_double,
                    probability=combined_prob
                )
            else:
                target_state = self._create_target_state(
                    target_field=target_field,
                    current_doubles=current_doubles,
                    is_double=is_double,
                    from_jail_card=is_jail_card
                )
                transitions[target_state] = transitions.get(target_state, 0) + combined_prob

    def _add_community_transitions(self,
                                   transitions: dict[MonopolyState, float],
                                   current_pos: int,
                                   current_doubles: int,
                                   is_double: bool,
                                   probability: float
                                   ) -> None:
        """
            Fügt alle möglichen Übergänge nach dem Ziehen einer Gemeinschaftskarte hinzu.

            Args:
                transitions: Dictionary, das modifiziert wird
                current_pos: Das Gemeinschaftsfeld (2, 17 oder 33)
                current_doubles: Aktueller Pasch-Zähler
                is_double: Wurde ein Pasch gewürfelt?
                probability: Wahrscheinlichkeit, auf diesem Feld zu landen
            """
        card_targets = self._get_community_targets(current_pos)

        for target_field, card_prob in card_targets.items():
            combined_prob = probability * card_prob

            # Prüfen ob "Gehe ins Gefängnis"-Karte
            is_jail_card = (target_field == self.jail_field)

            target_state = self._create_target_state(
                target_field=target_field,
                current_doubles=current_doubles,
                is_double=is_double,
                from_jail_card=is_jail_card
            )
            transitions[target_state] = transitions.get(target_state, 0) + combined_prob

    def _get_transitions_from_jail_state(self,
                                         state: MonopolyState
                                         ) -> dict[MonopolyState, float]:
        """
            Berechnet alle möglichen Übergänge von einem Gefängnis-Zustand.

            Args:
                state: Ausgangszustand (muss in_jail=True haben)

            Returns:
                Dictionary {Zielzustand: Wahrscheinlichkeit}
            """
        transitions = {}
        jail_round = state.counter  # 0 = Runde 1, 1 = Runde 2, 2 = Runde 3

        # Runde 1 oder 2: Nur Pasch befreit
        if jail_round < 2:
            # Kein Pasch → Bleibt im Gefängnis, nächste Runde
            prob_no_double = sum(self.non_doubles_probabilities.values())
            next_jail_state = MonopolyState(self.jail_field, jail_round + 1, True)
            transitions[next_jail_state] = prob_no_double

            # Pasch → Frei, zieht Würfelsumme, Zug endet (counter = 0)
            for dice_sum, prob in self.doubles_probabilities.items():
                if prob > 0:
                    target_field = self._calculate_target_field(self.jail_field, dice_sum)
                    self._add_jail_exit_transition(
                        transitions=transitions,
                        target_field=target_field,
                        probability=prob,
                        is_double=False  # Zug endet, kein Weiterwürfeln
                    )

        # Runde 3: Kommt auf jeden Fall raus
        else:
            # Kein Pasch → Frei, zieht Würfelsumme, Zug endet (counter = 0)
            for dice_sum, prob in self.non_doubles_probabilities.items():
                if prob > 0:
                    target_field = self._calculate_target_field(self.jail_field, dice_sum)
                    self._add_jail_exit_transition(
                        transitions=transitions,
                        target_field=target_field,
                        probability=prob,
                        is_double=False
                    )

            # Pasch → Frei, zieht Würfelsumme, darf nochmal würfeln (counter = 1)
            for dice_sum, prob in self.doubles_probabilities.items():
                if prob > 0:
                    target_field = self._calculate_target_field(self.jail_field, dice_sum)
                    self._add_jail_exit_transition(
                        transitions=transitions,
                        target_field=target_field,
                        probability=prob,
                        is_double=True  # Darf nochmal würfeln
                    )

        return transitions

    def _add_jail_exit_transition(self,
                                  transitions: dict[MonopolyState, float],
                                  target_field: int,
                                  probability: float,
                                  is_double: bool
                                  ) -> None:
        """
        Fügt Übergang(e) beim Verlassen des Gefängnisses hinzu.

        Args:
            transitions: Dictionary, das modifiziert wird
            target_field: Zielfeld nach dem Würfeln
            probability: Wahrscheinlichkeit dieses Wurfs
            is_double: Darf der Spieler nochmal würfeln? (nur Runde 3 + Pasch)
        """
        # Neuer Pasch-Zähler
        new_doubles = 1 if is_double else 0

        # Ereignisfeld
        if target_field in self.game_version.chance_fields:
            self._add_chance_card_transitions(
                transitions=transitions,
                current_pos=target_field,
                current_doubles=0,  # Aus Gefängnis kommend, startet bei 0
                is_double=is_double,
                probability=probability
            )
            return

        # Gemeinschaftsfeld
        if target_field in self.game_version.community_fields:
            self._add_community_transitions(
                transitions=transitions,
                current_pos=target_field,
                current_doubles=0,
                is_double=is_double,
                probability=probability
            )
            return

        # Normales Feld
        target_state = MonopolyState(target_field, new_doubles, False)
        transitions[target_state] = transitions.get(target_state, 0) + probability

    def create_transition_matrix(self, state_space: list[MonopolyState]) -> np.ndarray:
        """
            Erstellt die vollständige Übergangsmatrix.

            Args:
                state_space: Liste aller MonopolyState-Objekte (120 Zustände)

            Returns:
                np.ndarray: 120×120 Übergangsmatrix

            Note:
                - Zeile i entspricht Ausgangszustand state_space[i]
                - Spalte j entspricht Zielzustand state_space[j]
                - Jede Zeile summiert sich zu 1.0
            """
        n_states = len(state_space)
        transition_matrix = np.zeros((n_states, n_states))

        # Index-Lookup für schnellen Zugriff: MonopolyState → Index
        state_to_index = {state: idx for idx, state in enumerate(state_space)}

        # Für jeden Ausgangszustand
        for i, state in enumerate(state_space):

            # Übergänge berechnen basierend auf Zustandstyp
            if state.in_jail:
                transitions = self._get_transitions_from_jail_state(state)
            else:
                transitions = self._get_transitions_from_normal_state(state)

            # Übergänge in Matrix eintragen
            for target_state, probability in transitions.items():
                if target_state in state_to_index:
                    j = state_to_index[target_state]
                    transition_matrix[i, j] += probability
                else:
                    # Sollte nicht passieren - Debugging-Hinweis
                    print(f"Warnung: Zielzustand {target_state} nicht im state_space!")

        return transition_matrix


