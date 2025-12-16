def parse():
    import sys
    # return the command-line arguments (excluding the script name) as a list of strings
    input_data = {"content": []}
    for i in range(2, len(sys.argv), 2):
        input_data["content"].append({sys.argv[i]: sys.argv[i+1]})
    return sys.argv[1], input_data

if __name__ == "__main__":
    args = parse()
    from MyLm import call

    res = call(args[0], args[1])
    print(res)