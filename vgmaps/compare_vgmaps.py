import json, os, sys, glob

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    vgmaps = glob.glob("*.vgmap")
    if len(vgmaps) < 2:
        print("Not enough maps to compare!")
        sys.exit()
    elif len(vgmaps) == 2:
        first = vgmaps[0]
        second = vgmaps[1]
    else:
        print('More than two maps found!\n')
        for i in range(len(vgmaps)):
            print(str(i) + '. ' + vgmaps[i])
        first_num = -1
        while (first_num < 0) or (first_num >= len(vgmaps)):
            try:
                first_num = int(input("\nPlease pick first mesh to compare:  ")) - 1 
            except ValueError:
                pass
        first = vgmaps[first_num]
        second_num = -1
        while (second_num < 0) or (second_num >= len(vgmaps)):
            try:
                second_num = int(input("\nPlease pick first mesh to compare:  ")) - 1 
            except ValueError:
                pass
        second = vgmaps[second_num]
    with open(first, 'r') as f:
        first_data = json.loads(f.read())
    with open(second, 'r') as f:
        second_data = json.loads(f.read())
    differences = {}
    differences['not_in_'+first] = list(second_data.keys() - first_data.keys())
    differences['not_in_'+second] = list(first_data.keys() - second_data.keys())
    #with open('vgmap_differences.json', 'wb') as f:
        #f.write(json.dumps(differences, indent=4).encode("utf-8"))
    with open('not_in_' + first + '.json', 'wb') as f:
        f.write(json.dumps(differences['not_in_'+first], indent=4).encode("utf-8"))
    with open('not_in_' + second + '.json', 'wb') as f:
        f.write(json.dumps(differences['not_in_'+second], indent=4).encode("utf-8"))
