class GermanMonopoly:
    def __init__(self):
        self.board_fields = range(40)
        self.jail_field = 10
        self.go_in_jail_field = 30
        self.chance_fields = [7, 22, 36]
        self.community_fields = [2, 17, 33]
        self.railroads = [5, 15, 25, 35]
        self.chance_card_fixed_targets = [
            0,  # Los
            1,  # Badstraße
            5,  # Südbahnhof
            11,  # Seestraße
            24,  # Opernplatz
            39,  # Schlossallee
            10  # Gefängnis
        ]
        self.community_chest_fixed_targets = [
            0,  # Los
            10  # Gefängnis
        ]
        self.total_cards = 16
        self.position_changing_chance_cards = 9
        self.position_changing_community_cards = 2

    def get_next_railroad(self, current_field: int) -> int:
        for railroad in self.railroads:
            if railroad > current_field:
                return railroad
        return self.railroads[0]

    @staticmethod
    def get_three_back(self, current_field: int) -> int:
        return (current_field - 3) % 40

