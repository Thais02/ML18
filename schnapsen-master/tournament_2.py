import sys, random
from api import State, engine, util
from scipy import stats
import os
from os import path
from argparse import ArgumentParser


def run(botnames, myrepeats):
    verbose = False
    myphase = 1
    os.makedirs("tournament_results", exist_ok=True)
    filename = "tournament_results/tournament_results__"   # .txt
    start_seed = 69420
    seed_interval = 21

    # create new output file
    filenumber = 1
    new_filename = filename + str(filenumber) + ".txt"
    while path.exists(new_filename):
        filenumber += 1
        new_filename = filename + str(filenumber) + ".txt"
    file = open(new_filename, "w")

    file.write("start_seed=%s & seed_interval=%s\n" % (start_seed, seed_interval))

    # Create players
    bots = []
    for bot in botnames:
        bots.append(util.load_player(bot))
        file.write(bot + " | ")

    file.write("\n")

    n = len(bots)
    total_points = [0] * len(bots)
    wins = [0] * len(bots)
    matches = [(p1, p2) for p1 in range(n) for p2 in range(n) if p1 < p2]

    totalgames = (n*n - n)/2 * myrepeats
    playedgames = 0

    print('Playing {} games:'.format(int(totalgames)))
    file.write('Playing {} games:\n'.format(int(totalgames)))

    for a, b in matches:
        for r in range(myrepeats):

            if random.choice([True, False]):
                p = [a, b]
            else:
                p = [b, a]

            # generate modified seed
            seed = start_seed + seed_interval * (playedgames + 1)
            file.write("seed: " + str(seed) + "\t\t")

            # Generate a state with a random seed
            state = State.generate(phase=myphase, id=seed)

            winner, score = engine.play(bots[p[0]], bots[p[1]], state, 1000, verbose, True)

            if winner is not None:
                winner = p[winner - 1]
                total_points[winner] += score
                wins[winner] += 1

            playedgames += 1
            print('Played {} out of {:.0f} games ({:.0f}%): {} \r'.format(playedgames, totalgames, playedgames / float(totalgames) * 100, total_points))
            file.write('Played {} out of {:.0f} games ({:.0f}%): {} \r'.format(playedgames, totalgames, playedgames / float(totalgames) * 100, total_points))

    print('Results:')
    file.write("\nResults:\n")
    for i in range(len(bots)):
        print('    bot {}: {} points'.format(botnames[i], total_points[i]))
        file.write('bot {}: {} points\n'.format(botnames[i], total_points[i]))
        binom_test = stats.binom_test(wins[i], n=playedgames, p=0.5, alternative="greater")
        file.write("    wins(x)=%s, playedgames(n)=%s, p=0.5, alternative=greater\n" % (wins[i], playedgames))
        print("        Binomial test result: " + str(binom_test))
        file.write("    Binomial test result: " + str(binom_test) + "\n")
        if binom_test < 0.05:
            print("        Experiment passed binomial test")
            file.write("    Experiment passed binomial test\n")
        else:
            print("        Experiment failed binomial test (p-value is not smaller than 0.05)")
            file.write("    Experiment failed binomial test (p-value is not smaller than 0.05)\n")
    file.close()


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-p", "--players",
                        dest="players",
                        help="Comma-separated list of player names (enclose with quotes).",
                        default="ourbot,rdeep")
    parser.add_argument("-r", "--repeats",
                        dest="repeats",
                        help="How many matches to play for each pair of bots",
                        type=int, default=100)
    parser.add_argument("-a",
                        dest="runs",
                        help="How many tournaments are ran",
                        type=int, default=1)

    arg_botnames = parser.parse_args().players.split(",")
    arg_repeats = parser.parse_args().repeats
    arg_runs = parser.parse_args().runs

    for i in range(0, arg_runs):
        run(arg_botnames, arg_repeats)
