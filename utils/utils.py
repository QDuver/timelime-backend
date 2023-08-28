def number_to_ordinal(n):
    ordinals = {
        1: "first",
        2: "second",
        3: "third",
        # Add more mappings as needed
    }
    
    return ordinals.get(n, str(n) + "th")  # Default to "nth" for unsupported numbers