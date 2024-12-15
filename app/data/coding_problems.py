CODING_PROBLEMS = [
    {
        "title": "Find the First Unique Character",
        "difficulty": "Easy",
        "problem": "Given a string, find the first non-repeating character and return its index. If all characters repeat, return -1.",
        "code": """
def get_first_non_repeating_character(str):
    char_map = {}
    for index, char in enumerate(str):
        if char in char_map:
            char_map[char]['count'] += 1
        else:
            char_map[char] = {'count': 1, 'index': index}
    
    for char in char_map:
        if char_map[char]['count'] == 1:
            return char_map[char]['index']
    return -1

#Test cases
assert(get_first_non_repeating_character("") == -1)
assert(get_first_non_repeating_character("jj") == -1)
assert(get_first_non_repeating_character("jithu") == 0)
assert(get_first_non_repeating_character("jithuj") == 1)

            """,
    },
    {
        "title": "Merge Overlapping Intervals",
        "difficulty": "Easy",
        "problem": "Given a list of intervals, merge overlapping intervals and return the merged intervals.",
        "code": """
def merge_overlapping_intervals(intervals):
    intervals.sort()
    final_intervals = []

    current = intervals[0]
    i = 1
    while i < len(intervals):
        next = intervals[i]
        if next[0] <= current[1]:
            current[1] = max(current[1], next[1])
        else:
            final_intervals.append(current)
            current = next
        i += 1
    final_intervals.append(current)

    return final_intervals

# Test cases
assert merge_overlapping_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [
    [1, 6],
    [8, 10],
    [15, 18],
]

assert merge_overlapping_intervals([[1, 4], [4, 5]]) == [[1, 5]]

assert merge_overlapping_intervals([[1, 5], [3, 4]]) == [[1, 5]]
    
                    """,
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "problem": "Find the length of the longest substring in a given string that contains no repeating characters.\n\nInput:\nstring = 'abcabcbb'\nOutput:\n3 (substring 'abc')",
        "code": """
def fun(s):
    char_set = set()
    start = 0
    max_length = 0

    for end in range(len(s)):
        while s[end] in char_set:
            char_set.remove(s[start])
            start += 1

        char_set.add(s[end])

        max_length = max(max_length, end - start + 1)

    return max_length

# Test cases
assert fun("abcabcbb") == 3
assert fun("bbbbb") == 1
assert fun("") == 0
        """,
    },
    {
        "title": "Coin Change Problem",
        "difficulty": "Hard",
        "problem": "You are given an integer array coins representing coin denominations and an integer amount representing the total amount.\nReturn the fewest number of coins that make up the amount. If it’s not possible, return -1.",
        "code": """
def coin_change(coins: list[int], amount: int) -> int:
    # Initialize the dp array with a large value (inf)
    min_coins = [float("inf")] * (amount + 1)
    min_coins[0] = 0  # Base case: 0 coins are needed to make amount 0

    # Iterate through all amounts from 1 to amount
    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0:  # Only consider valid subproblems
                min_coins[i] = min(min_coins[i], min_coins[i - coin] + 1)

    # If min_coins[amount] is still inf, it means no combination of coins can make the amount
    return min_coins[amount] if min_coins[amount] != float("inf") else -1

# Test cases
assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
assert coin_change([186, 419, 83, 408], 6249) == 20
        """,
    },
]
