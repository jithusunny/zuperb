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
        """,
    },
]
