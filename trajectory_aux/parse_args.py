import sys, argparse, uuid

def parse_args():
    if '--' in sys.argv:
        argv = sys.argv[sys.argv.index('--') + 1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('-data_csv', '--data_csv', dest='data_csv', metavar='FILE')
        parser.add_argument('-output', '--output', dest='output', metavar='FILE', default=f'/tmp/{uuid.uuid1()}.jpeg')
        args = parser.parse_known_args(argv)[0]
        print('data_csv: ', args.data_csv)
        print('output: ', args.output)
    return args