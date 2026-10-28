# This program was developed to determine the name of the local unit of
# The Dark Empire costuming club from votes of the membership, choosing between
# six options proposed by the same membership. These names are hard-coded
# variables in this program. The top three names will go to the leadership of
# The Dark Empire for vetting and approval.
#
# Author: Skylar Gurnett
# January 2026
#
# Note: The first winner output given by this program was denied by The Dark
# Empire leadership. The second choice winner was then considered, and later
# approved. The local unit was named Onyx Spire and launched in March 2026.

from collections import Counter

def droop_quota(num_valid_votes, seats):
    return (num_valid_votes // (seats + 1)) + 1


def clean_ballots(ballots, continuing):
    cleaned = []
    for ballot in ballots:
        new_ballot = [c for c in ballot if c in continuing]
        if new_ballot:
            cleaned.append(new_ballot)
    return cleaned


def count_first_preferences(weighted_ballots, continuing):
    counts = Counter()
    for ballot, weight in weighted_ballots:
        if ballot and ballot[0] in continuing:
            counts[ballot[0]] += weight
    return counts


def transfer_surplus(weighted_ballots, elected, surplus, continuing, verbose):
    contributing = [(b, w) for (b, w) in weighted_ballots if b and b[0] == elected]

    if not contributing or surplus <= 0:
        return weighted_ballots

    total_weight = sum(w for _, w in contributing)
    if total_weight == 0:
        return weighted_ballots

    transfer_value = surplus / total_weight

    if verbose:
        print(f"\n  Transferring surplus of {elected}:")
        print(f"    surplus = {surplus:.6f}")
        print(f"    total weight = {total_weight:.6f}")
        print(f"    transfer value = {transfer_value:.6f}")

    new_weighted = []
    for ballot, weight in weighted_ballots:
        if ballot and ballot[0] == elected:
            new_weight = weight * transfer_value
        else:
            new_weight = weight

        new_ballot = [c for c in ballot if c != elected]
        new_weighted.append((new_ballot, new_weight))

    return new_weighted

#deterministic tie breaker to eliminate candidate most often ranked last
#note: this is how I elected to handle this case, not necessarily representative
#of how any one stv system handles it
def tie_break_last_place(weighted_ballots, continuing, tied):
    last_place_counts = {c: 0 for c in tied}

    for ballot, weight in weighted_ballots:
        ranked = [c for c in ballot if c in continuing]
        if ranked:
            last = ranked[-1]
            if last in last_place_counts:
                last_place_counts[last] += weight

    worst = max(last_place_counts.values())
    worst_candidates = [c for c, v in last_place_counts.items() if v == worst]

    if len(worst_candidates) == 1:
        return worst_candidates[0]

    #final fallback: alphabetical
    return sorted(worst_candidates)[0]


def recount(ballots, continuing, seats_remaining, elected, verbose, fixed_quota, round_num=1):
    cleaned = clean_ballots(ballots, continuing)
    weighted_ballots = [(b, 1.0) for b in cleaned]

    while seats_remaining > 0 and continuing:
        if verbose:
            print(f"\n=== ROUND {round_num} ===")
            print(f"Continuing: {sorted(continuing)}")

        counts = count_first_preferences(weighted_ballots, continuing)

        if verbose:
            print(f"Quota (fixed): {fixed_quota}")
            print("First preferences:")
            for c in sorted(continuing):
                print(f"  {c}: {counts[c]:.4f}")

        # Elect candidates meeting quota
        winners = [c for c in continuing if counts[c] >= fixed_quota]

        if winners:
            # Elect in descending order of tally
            winners_sorted = sorted(winners, key=lambda c: (-counts[c], c))

            for w in winners_sorted:
                if seats_remaining == 0:
                    break

                surplus = counts[w] - fixed_quota

                if verbose:
                    print(f"\nCandidate {w} elected with surplus {surplus:.4f}")

                elected.append(w)
                continuing.remove(w)
                seats_remaining -= 1

                weighted_ballots = transfer_surplus(
                    weighted_ballots, w, surplus, continuing, verbose
                )

            round_num += 1
            continue

        #no winner → eliminate lowest
        min_count = min(counts[c] for c in continuing)
        lowest_group = [c for c in continuing if counts[c] == min_count]

        if len(lowest_group) == 1:
            lowest = lowest_group[0]
        else:
            lowest = tie_break_last_place(weighted_ballots, continuing, lowest_group)

        if verbose:
            print(f"\nNo candidate reached quota.")
            print(f"Eliminating: {lowest}")

        continuing.remove(lowest)

        #restart entire count (Wright)
        return recount(
            ballots,
            continuing,
            seats_remaining,
            elected,
            verbose,
            fixed_quota,
            round_num + 1
        )

    return elected


def wright_stv(ballots, seats, verbose=False):
    total_valid = len(ballots)
    fixed_quota = droop_quota(total_valid, seats)

    if verbose:
        print(f"Total ballots: {total_valid}")
        print(f"Seats: {seats}")
        print(f"Fixed Droop quota: {fixed_quota}\n")

    candidates = set(c for ballot in ballots for c in ballot)
    continuing = set(candidates)
    elected = []

    return recount(ballots, continuing, seats, elected, verbose, fixed_quota)


def main():
    ballots = [
        ["Pinnacle", "Summit Crest", "Kruva", "Onyx", "Mountain", "Drassh"],
        ["Summit Crest", "Onyx", "Mountain", "Pinnacle", "Kruva", "Drassh"],
        ["Kruva", "Mountain", "Drassh", "Onyx", "Summit Crest", "Pinnacle"],
        ["Kruva", "Pinnacle", "Drassh", "Onyx", "Mountain", "Summit Crest"],
        ["Kruva", "Mountain", "Drassh", "Pinnacle", "Onyx", "Summit Crest"],
        ["Kruva", "Onyx", "Drassh", "Mountain", "Pinnacle", "Summit Crest"],
        ["Onyx", "Kruva", "Mountain", "Drassh", "Summit Crest", "Pinnacle"],
        ["Onyx", "Drassh", "Kruva", "Pinnacle", "Summit Crest", "Mountain"],
        ["Summit Crest", "Kruva", "Mountain", "Pinnacle", "Onyx", "Drassh"],
    ]

    winners = wright_stv(ballots, seats=3, verbose=True)
    print("\nElected:", winners)


if __name__ == "__main__":
    main()