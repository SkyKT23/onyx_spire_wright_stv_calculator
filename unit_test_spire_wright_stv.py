# Unit test developed for spire_wright_stv.py to verify the program operates
# according to Wright STV method rules. Note: test inputs were validated with
# manual calculations.
#
# Author: Skylar Gurnett
# February 2026

def test_single_seat_with_different_candidate_names(self):
    ballots = [
        ["Falcon", "Orion"],
        ["Falcon", "Orion"],
        ["Orion", "Falcon"],
        ["Falcon", "Orion"],
    ]

    result = spire_wright_stv(ballots, seats=1)

    self.assertEqual(result, ["Falcon"])