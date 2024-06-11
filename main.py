from grammar import origin_productions, null

terminals: list[str] = []
non_terminals: list[str] = []
start_symbol: list[str] = []
other_symbol: list[str] = []

first: dict[str, set[str]] = {}
follow: dict[str, set[str]] = {}
productions: dict[str, list[list[str]]] = {}
table: dict[tuple[str, str], str] = {}
end_symbol = "$"


def init():
    global terminals, non_terminals
    global start_symbol, other_symbol
    global first, follow
    global productions

    # init_production
    def to_list(strs: list[str]):
        return [str.split(" ") for str in strs]

    for key, value in origin_productions.items():
        productions[key] = to_list(value)

    # init symbols
    non_terminals = list(productions.keys())
    start_symbol = non_terminals[:1]
    other_symbol = non_terminals[1:]
    terminals = list(
        set(
            [
                symbol
                for list_list_symbol in productions.values()
                for list_symbol in list_list_symbol
                for symbol in list_symbol
                if symbol not in non_terminals
            ]
        )
    )
    terminals.append(end_symbol)

    # init first set and follow set
    for symbol in terminals:
        # if a symbol is a final symbol, then FIRST[symbol] = [symbol]
        first[symbol] = set([symbol])
        follow[symbol] = set([])
    for symbol in start_symbol:
        first[symbol] = set([])
        # put end char to FOLLOW[start symbol]
        follow[symbol] = set([end_symbol])
    for symbol in other_symbol:
        first[symbol] = set([])
        follow[symbol] = set([])


def isFinal(x: str):
    return x in terminals


def dislocation(x: list[str]):
    """
    turn

    1, 2, 3, 4

    into

    ([], 1), ([1], 2),  ([1, 2], 3),  ([1, 2, 3], 4)
    """
    return [(x[: i], x[i]) for i in range(len(x))]


def allHasNull(symbol_list: list[str]):
    all_null = True
    for symbol in symbol_list:
        if null not in first[symbol]:
            all_null = False
            break
    return all_null


def discardNull(tk_set: set[str]):
    tmp = set(tk_set)
    tmp.discard(null)
    return set(tmp)


def getFirst(tk_list: list[str]):
    """
    get the first set of list[token]
    """
    l = [set(first[tk_list[0]])] if len(tk_list) > 0 else []
    if len(tk_list) >= 2:
        for prev, this in dislocation(tk_list):
            if allHasNull(prev) is True:
                first_set = set(first[this])
                l.append(set(first_set))
            else:
                break
    ret: set[str] = set()
    for i in l:
        ret.update(i)
    return ret


def set_first():
    while True:
        add = False
        for non_terminal, production_list in productions.items():
            if isFinal(non_terminal) is not True:
                for production in production_list:
                    # if X -> null is a production, then add null to first[X]
                    if production == [null]:
                        add |= False if null in first[non_terminal] else True
                        first[non_terminal].add(null)
                    else:
                        # for X -> abc, if a -> null, then add first[b] to first[X] exclude null
                        for prev, this in dislocation(production):
                            if allHasNull(prev) is True:
                                first_set = discardNull(first[this])
                                add |= False if first_set.issubset(first[non_terminal]) else True
                                first[non_terminal].update(first_set)
                            else:
                                break

                        # for X -> abc, if a, b, c -> null, then add null to first[X]
                        if allHasNull(production) is True:
                            add |= True if null not in first[non_terminal] else False
                            first[non_terminal].add(null)
        if add is False:
            break


def set_follow():
    while True:
        add = False
        for non_terminal, production_list in productions.items():
            for production in production_list:
                if len(production[:-1]) > 0:
                    for i in range(0, len(production[:-1])):
                        # for X -> aBc, add first[c] to follow[B] exclude null
                        follow_set = discardNull(getFirst(production[i + 1 :]))
                        add |= False if follow_set.issubset(follow[production[i]]) else True
                        follow[production[i]].update(follow_set)

                        # if c includes null, then add follow[X] to follow[B]
                        if allHasNull(production[i + 1 :]):
                            add |= (
                                False
                                if follow[non_terminal].issubset(follow[production[i]])
                                else True
                            )
                            follow[production[i]].update(follow[non_terminal])

                # for X -> aB, add follow[X] to follow[B]
                add |= False if follow[non_terminal].issubset(follow[production[-1]]) else True
                follow[production[-1]].update(follow[non_terminal])
        if add == False:
            break


def gen_table():
    for terminal in discardNull(set(terminals)):
        for non_terminal in non_terminals:
            table[(non_terminal, terminal)] = ""

    for symbol, production_list in productions.items():
        for production in production_list:
            for x in discardNull(getFirst(production)):
                table[(symbol, x)] += f"{symbol} -> {' '.join(production)}"
            if null in getFirst(production):
                for x in follow[symbol]:
                    table[(symbol, x)] += f"{symbol} -> {' '.join(production)}"


def save_table():
    input_symbol = [terminal for terminal in terminals]
    input_symbol.remove(null)
    input_symbol.sort()

    filename = f"./table.csv"

    with open(filename, "w", encoding="utf-8") as file:
        line1 = f"non-terminal,"
        for terminal in input_symbol:
            line1 += terminal + ","
        file.write(line1 + "\n")
        for terminal in start_symbol + other_symbol:
            line = terminal + ","
            for non_terminal in input_symbol:
                line += table[(terminal, non_terminal)] + ","
            file.write(line + "\n")


if __name__ == "__main__":
    init()
    set_first()
    set_follow()
    gen_table()
    save_table()
